CREATE TABLE agents
(
    id TEXT PRIMARY KEY,
    user TEXT NOT NULL,
    grade TEXT NOT NULL,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    matricule TEXT NOT NULL,
    unit TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    tel TEXT NOT NULL,
    adresse TEXT NOT NULL
)

CREATE TABLE agents_habilitations
(
    id TEXT PRIMARY KEY,
    convoyeur TEXT NOT NULL DEFAULT 'N',
    sniper TEXT NOT NULL DEFAULT 'N',
    CHV TEXT NOT NULL DEFAULT 'N',
    perquise TEXT NOT NULL DEFAULT 'N',
    opj TEXT NOT NULL DEFAULT 'N'
);

CREATE TABLE civils
(
    idcivil INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    tel TEXT NOT NULL,
    adresse TEXT NOT NULL
);

CREATE TABLE vehicules
(
    idvehicule INTEGER PRIMARY KEY AUTOINCREMENT,
    marque TEXT NOT NULL,
    modele TEXT NOT NULL,
    couleur TEXT NOT NULL,
    plaque TEXT NOT NULL,
    nomprop TEXT NOT NULL,
    prenomprop TEXT NOT NULL
);

CREATE TABLE armes
(
    idarme INTEGER PRIMARY KEY AUTOINCREMENT,
    modele TEXT NOT NULL,
    numserie TEXT NOT NULL,
    nomprop TEXT NOT NULL,
    prenomprop TEXT NOT NULL,
    statut TEXT NOT NULL
);


 