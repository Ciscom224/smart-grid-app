// 1. Trouver le bâtiment servant de centre
MATCH (found_center:Building)
WHERE (toLower(found_center.adresse) CONTAINS toLower($search_term) OR found_center.code_commune = $search_term)
WITH found_center LIMIT 1

// 2. Identifier tous les bâtiments dans le rayon défini
MATCH (b:Building)
WHERE point.distance(point({latitude: b.latitude, longitude: b.longitude}), 
                     point({latitude: found_center.latitude, longitude: found_center.longitude})) < $radius

// 3. Filtrer par distance au réseau et consommation minimale
MATCH (b)-[r:CONNECTED]->(g:GridSegment)
WHERE r.distance >= $dist_min AND r.distance <= $dist_max
  AND b.conso_totale >= $min_conso

OPTIONAL MATCH (b)-[:HAS_POTENTIAL]->(p:Potentiel)
OPTIONAL MATCH (b)-[:HAS_PROFIL]->(pr:Profil)

WITH b, r, found_center, 
     coalesce(p.prod_annuelle_mwh, 0) as prod_val,
     pr, p

// 4. Calcul de l'autosuffisance individuelle (pour info dans la liste)
WITH *, CASE WHEN b.conso_totale > 0 THEN (prod_val / b.conso_totale) * 100 ELSE 0 END as current_asuff

// 5. Agrégation temporaire pour calculer les KPIs totaux du cluster
WITH found_center,
     sum(b.conso_totale) as cluster_total_conso,
     sum(prod_val) as cluster_total_prod,
     count(b) as nb_b,
     collect({
        b: b, 
        r: r, 
        pr: pr, 
        p: p, 
        prod_val: prod_val, 
        asuff: current_asuff
     }) as cluster_items

// 6. FILTRE CRITIQUE : Autosuffisance GLOBALE et Mixité
// On calcule le ratio sur le total du groupe
WITH *, 
     CASE WHEN cluster_total_conso > 0 
          THEN (cluster_total_prod / cluster_total_conso) * 100 
          ELSE 0 END as cluster_autosuff_ratio
WHERE cluster_autosuff_ratio >= $min_autosuff
  AND nb_b >= $min_buildings
  // On vérifie qu'il y a au moins un consommateur pur dans les items collectés
  AND size([x IN cluster_items WHERE x.prod_val < 0.1]) >= 1

// 7. Reconstruction finale du résultat
RETURN {
    kpi: {
        total_conso: cluster_total_conso,
        total_prod: cluster_total_prod,
        nb_batiments: nb_b,
        nb_prosumers: size([x IN cluster_items WHERE x.prod_val > 0.1]),
        autosuffisance: cluster_autosuff_ratio
    },
    liste_batiments: [x IN cluster_items | {
        uid: x.b.uid,
        adresse: x.b.adresse,
        lat: x.b.latitude,
        lon: x.b.longitude,
        type: labels(x.b),        
        conso: x.b.conso_totale,
        prod: x.prod_val,
        autosuffisance: x.asuff,
        dist_grid: toFloat(x.r.distance),
        load_curve_json: x.pr.load_curve,       
        prod_curve_json: x.p.courbe_charge
    }],
    centre: { 
        lat: found_center.latitude, 
        lon: found_center.longitude, 
        adresse: found_center.adresse 
    }
} as Resultat