
  window.addEventListener('scroll', function() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var parallaxElements = document.querySelectorAll('.parallax');

    for (var i = 0; i < parallaxElements.length; i++) {
      var parallaxElement = parallaxElements[i];
      var parallaxOffset = parallaxElement.offsetTop - window.innerHeight;
      var parallaxScrollTop = scrollTop - parallaxOffset;

      if (parallaxScrollTop > 0 && parallaxScrollTop < window.innerHeight) {
        parallaxElement.style.backgroundPositionY = -(parallaxScrollTop / 2) + 'px';
      }
    }
  });
