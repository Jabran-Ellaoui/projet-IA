// Fonction pour rediriger vers la page du jeu
function startGame() {
    document.querySelector('.container').style.animation = "fadeOut 0.8s forwards";
    
    setTimeout(() => 
        {
        window.location.href = "game"; // Si on avait game.html, on aurait pas le lien de la view "game"
    }, 800);
}

// Animation de fondu en sortie
document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.container').style.animation = "slideDown 1.5s ease-in-out forwards";
}
);

window.addEventListener('pageshow', (event) => { // Permet de refresh l'animation en cas de retour arrière
    if (event.persisted) {  // Vérifie si la page est chargée depuis le cache
        document.querySelector('.container').style.animation = "slideDown 1.5s ease-in-out forwards";
    }
});