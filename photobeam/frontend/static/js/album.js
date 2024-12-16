document.addEventListener("DOMContentLoaded", function () {
    const slickModal = document.getElementById("slideshow-modal");
    const slideshowContent = document.querySelector(".slideshow-content");

    let slickInitialized = false;

    function initSlick() {
        if (!slickInitialized) {
            $(slideshowContent).slick({
                infinite: true,
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: true,
                dots: true,
                adaptiveHeight: true,
                prevArrow: '.slideshow-prev',
                nextArrow: '.slideshow-next',
                speed: 0,
                cssEase: 'none', 
            });
            slickInitialized = true;
        }
    }

    window.openSlideshow = function (startIndex) {
        slickModal.style.display = "flex";

        initSlick();

        $(slideshowContent).slick("slickGoTo", startIndex);
    };

    window.closeSlideshow = function () {
        slickModal.style.display = "none";

        $(slideshowContent).slick("slickPause"); 
    };

    document.querySelector(".slideshow-prev").addEventListener("click", (e) => e.preventDefault());
    document.querySelector(".slideshow-next").addEventListener("click", (e) => e.preventDefault());
});
