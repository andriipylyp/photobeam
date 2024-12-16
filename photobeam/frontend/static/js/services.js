$(document).ready(function () {
    $('.slick-slider').slick({
    slidesToShow: 3, 
    slidesToScroll: 1, 
    infinite: true, 
    autoplay: true, 
    autoplaySpeed: 5000, 
    arrows: false, 
    dots: true, 
    responsive: [
        {
        breakpoint: 768, 
        settings: {
            slidesToShow: 2
        }
        },
        {
        breakpoint: 480, 
        settings: {
            slidesToShow: 1
        }
        }
    ]
    });
});