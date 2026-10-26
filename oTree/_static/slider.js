// The answer is copied into a hidden field once the participant clicks or drags
document.querySelectorAll('.survey-slider').forEach(function (sl) {
    var field = sl.dataset.field;
    function record() {
        sl.classList.remove('untouched');
        document.getElementById('hidden_' + field).value = sl.value;
        var v = document.getElementById('value_' + field);
        v.textContent = 'Your answer: ' + sl.value;
        v.classList.add('answered');
        document.getElementById('missing_' + field).style.display = 'none';
    }
    sl.addEventListener('input', record);
    sl.addEventListener('change', record);
    sl.addEventListener('pointerup', record);   // a click exactly on the middle does not fire 'input'
});

// Do not submit while a slider has not been answered
var sliderForm = document.getElementById('form') || document.querySelector('form');
sliderForm.addEventListener('submit', function (e) {
    var missing = false;
    document.querySelectorAll('.survey-slider').forEach(function (sl) {
        if (document.getElementById('hidden_' + sl.dataset.field).value === '') {
            document.getElementById('missing_' + sl.dataset.field).style.display = 'block';
            missing = true;
        }
    });
    if (missing) {
        e.preventDefault();
        setTimeout(function () {
            document.querySelectorAll('button').forEach(function (b) { b.disabled = false; });
        }, 100);
    }
});