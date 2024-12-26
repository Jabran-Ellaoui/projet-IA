const background = document.querySelector('.background-cubes');

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}


function createCubes() {
    const totalCubes = 200; 
    const cubes = []; 

    for (let i = 0; i < totalCubes; i++) {
        const cube = document.createElement('div');
        cube.classList.add('cube');
        
        // Positionnement initial aléatoire
        const xPos = Math.random() * 100; // Position horizontale
        const yPos = Math.random() * 100; // Position verticale
        cube.style.left = `${xPos}vw`;
        cube.style.top = `${yPos}vh`;

        cube.style.backgroundColor = getRandomColor();

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
        });
        requestAnimationFrame(updateCubes); // MAJ des positions à chaque frame
    }

    updateCubes();
}

createCubes();