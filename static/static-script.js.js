// Reloj en vivo
function actualizarReloj() {
    const ahora = new Date();
    document.getElementById('reloj').innerText = `Hora actual: ${ahora.toLocaleTimeString()}`;
}
setInterval(actualizarReloj, 1000);
actualizarReloj();

// Validación en tiempo real para formularios
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', () => {
        if (input.value.trim() === '') {
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });
});

// Animaciones en botones
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.style.transform = 'scale(0.95)';
        setTimeout(() => btn.style.transform = 'scale(1)', 150);
    });
});