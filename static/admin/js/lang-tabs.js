(function($) {
  $(function() {
    var $select = $("#modeltranslation-main-switch");
    if (!$select.length) return;

    // Скрываем оригинальный селект
    $select.hide();

    
    // Получаем языки из опций
    var langs = [];
    $select.find("option").each(function() {
      langs.push({
        code: $(this).val(),
        label: $(this).text()
      });
    });

    // Создаем контейнер для кнопок
    var $btnWrap = $("<div/>", { class: "lang-button-switch" }).insertBefore($select);

    // Функция для обновления активной кнопки
    function setActive(code) {
      $btnWrap.find("button").removeClass("active");
      $btnWrap.find("button[data-lang='" + code + "']").addClass("active");
    }

    // Создаем кнопки
    langs.forEach(function(lang) {
      var $btn = $("<button/>", {
        type: "button",
        text: lang.label,
        "data-lang": lang.code,
        class: "lang-btn",
      }).appendTo($btnWrap);

      $btn.on("click", function() {
        // Меняем значение селекта и триггерим change
        $select.val(lang.code).trigger("change");
        setActive(lang.code);
      });
    });

    // Устанавливаем изначально активную
    setActive($select.val());
  });
})(django.jQuery);
