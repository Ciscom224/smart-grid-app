// 1. Récupération des bâtiments et de leurs segments de réseau
MATCH (g:GridSegment)<-[r:CONNECTED]-(b:Building)
WHERE b.latitude IS NOT NULL AND b.longitude IS NOT NULL
  AND r.distance >= $dist_min AND r.distance <= $dist_max
  AND b.conso_totale >= $min_conso

// 2. Récupération de l'énergie potentielle (Solaire)
OPTIONAL MATCH (b)-[:HAS_POTENTIAL]->(p:Potentiel)
WITH g, b, coalesce(p.prod_annuelle_mwh, 0) as prod_val

// 3. Agrégation par Segment (Le Cluster)
// On calcule les totaux directement ici pour définir la performance du cluster
WITH g, 
     count(b) as nb_b, 
     sum(b.conso_totale) as g_conso, 
     sum(prod_val) as g_prod,
     // Identification des consommateurs purs (production négligeable)
     sum(CASE WHEN prod_val < 0.1 THEN 1 ELSE 0 END) as nb_cons,
     collect({
        adresse: b.adresse,
        lat: b.latitude,
        lon: b.longitude,
        conso: round(b.conso_totale, 2),
        prod: round(prod_val, 2),
        type: labels(b)
     }) as batiments

// 4. Filtrage basé sur les performances GLOBALES du cluster
// On calcule le ratio sur les sommes (g_prod / g_conso)
WITH *, 
     CASE WHEN g_conso > 0 THEN (g_prod / g_conso) * 100 ELSE 0 END as cluster_ratio
WHERE nb_cons >= 1                       // Au moins un consommateur dans le groupe
  AND cluster_ratio >= $min_autosuff     // Le cluster doit atteindre le seuil global
  AND nb_b >= $min_buildings             // Taille minimale du cluster

// 5. Calcul des KPIs pour l'ensemble de la sélection territoriale
WITH collect({
    g: g,
    g_conso: g_conso,
    g_prod: g_prod,
    nb_b: nb_b,
    nb_cons: nb_cons,
    ratio: cluster_ratio,
    batiments: batiments
}) as all_clusters

// Réduction pour obtenir les totaux de tous les clusters validés
WITH all_clusters,
     reduce(s = 0.0, c IN all_clusters | s + c.g_conso) as total_conso_territoire,
     reduce(s = 0.0, c IN all_clusters | s + c.g_prod) as total_prod_territoire,
     reduce(s = 0, c IN all_clusters | s + c.nb_b) as total_nb_batiments

// 6. Construction du JSON final
RETURN {
    kpi_global_cluster: {
        total_conso: round(total_conso_territoire, 2),
        total_prod: round(total_prod_territoire, 2),
        nb_batiments: total_nb_batiments,
        autosuffisance: CASE WHEN total_conso_territoire > 0 
                             THEN round((total_prod_territoire / total_conso_territoire) * 100, 2) 
                             ELSE 0 END
    },
    centre: { adresse: "Vue Globale", lon: null, lat: null },
    clusters: apoc.map.fromPairs([item IN all_clusters | [
        "cluster_" + replace(item.g.nom_grd, " ", "_") + "_" + elementId(item.g), 
        {
            Kpi: {
                total_prod: round(item.g_prod, 2),
                total_conso: round(item.g_conso, 2),
                autosuffisance: round(item.ratio, 2),
                nb_batiments: item.nb_b,
                nb_consumers: item.nb_cons,
                nom: item.g.nom_grd,
                id_segment: elementId(item.g)
            },
            liste_batiments: item.batiments
        }
    ]])
} as Resultat