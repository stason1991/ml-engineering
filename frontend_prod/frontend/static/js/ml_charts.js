document.addEventListener('DOMContentLoaded', function() {
    console.log("Career Path Pro: Модуль визуализации загружен");

    // Функция для анимации прогресс-баров
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        let width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = width;
        }, 300);
    });
});