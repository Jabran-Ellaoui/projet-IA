// Sélection du conteneur
const background = document.querySelector('.background-cubes');

// Fonction pour générer une couleur aléatoire
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Fonction pour créer des cubes animés
function createCubes() {
    const totalCubes = 50; // Nombre total de cubes
    const cubes = []; // Tableau pour stocker les cubes

    for (let i = 0; i < totalCubes; i++) {
        const cube = document.createElement('div');
        cube.classList.add('cube');
        
        // Positionnement initial aléatoire
        const xPos = Math.random() * 100; // Position horizontale
        const yPos = Math.random() * 100; // Position verticale
        cube.style.left = `${xPos}vw`;
        cube.style.top = `${yPos}vh`;

        // Application d'une couleur aléatoire à chaque cube
        cube.style.backgroundColor = getRandomColor();

        // Vitesse initiale aléatoire
        const speedX = (Math.random() - 0.5) * 1; // Vitesse horizontale aléatoire
        const speedY = (Math.random() - 0.5) * 1; // Vitesse verticale aléatoire

        // Stockage des propriétés du cube
        cubes.push({ cube, xPos, yPos, speedX, speedY });

        background.appendChild(cube);
    }

    // Fonction de mise à jour de la position de chaque cube
    function updateCubes() {
        cubes.forEach((item) => {
            // Déplacer le cube
            item.xPos += item.speedX;
            item.yPos += item.speedY;

            // Si le cube touche les bords de l'écran, rebondir
            if (item.xPos <= 0 || item.xPos >= 100) item.speedX *= -1; // Rebond horizontal
            if (item.yPos <= 0 || item.yPos >= 100) item.speedY *= -1; // Rebond vertical

            // Déplacer le cube visuellement
            item.cube.style.left = `${item.xPos}vw`;
            item.cube.style.top = `${item.yPos}vh`;

            // Vérifier les collisions entre cubes
            cubes.forEach((otherItem) => {
                if (item !== otherItem) {
                    const dx = item.xPos - otherItem.xPos;
                    const dy = item.yPos - otherItem.yPos;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    // Si la distance entre deux cubes est inférieure à 3 (pour simuler une collision)
                    if (distance < 3) {
                        // Séparer légèrement les cubes après une collision pour éviter qu'ils se bloquent
                        const overlapX = (3 - distance) * (dx / distance);
                        const overlapY = (3 - distance) * (dy / distance);

                        item.xPos += overlapX;
                        item.yPos += overlapY;

                        // Inverser la direction des cubes pour simuler un rebond
                        item.speedX *= -1;
                        item.speedY *= -1;
                    }
                }
            });
        });
        requestAnimationFrame(updateCubes); // Mettre à jour les positions à chaque frame
    }

    updateCubes(); // Lancer l'animation
}

// Générer les cubes
createCubes();
