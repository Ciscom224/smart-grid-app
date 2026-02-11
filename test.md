"""' 
LOAD CSV WITH HEADERS FROM 'file:///profils.csv' AS row
// 1. FILTRE DE SÉCURITÉ (Crucial pour éviter l'erreur 22N31)
// On ignore toute ligne qui n'a pas d'adresse ou de courbe
WITH row WHERE row.adresse IS NOT NULL AND row.courbe_24h IS NOT NULL

CALL (row) {
    // 2. Création du Nœud Bâtiment
    MERGE (b:Building {id: row.adresse})
    
    // 3. Création du Nœud Profil (ID = Adresse + Mois)
    MERGE (p:LoadProfile {id: row.adresse + "_" + row.mois})
    SET 
        p.mois = toInteger(row.mois),
        // On transforme "32.8;31.5..." en liste de nombres [32.8, 31.5...]
        p.courbe_24h = [x IN split(row.courbe_24h, ';') | toFloat(x)],
        p.source = row.source

    // 4. Création du lien
    MERGE (b)-[r:HAS_PROFILE]->(p)
    SET r.annee = 2022
} IN TRANSACTIONS OF 1000 ROWS;
""'