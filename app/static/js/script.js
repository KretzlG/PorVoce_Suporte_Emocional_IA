document.addEventListener('DOMContentLoaded', () => {
    const moodCards = document.querySelectorAll('.mood-card');

    moodCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove a classe 'selected' de todos os cards
            moodCards.forEach(c => c.classList.remove('selected'));

            // Adiciona a classe 'selected' ao card clicado
            card.classList.add('selected');

            // Aqui você pode adicionar a lógica para enviar a seleção para o servidor,
            // por exemplo, usando uma chamada fetch() ou AJAX.
            // Exemplo: console.log(`O usuário selecionou: ${card.dataset.mood}`);
        });
    });
});