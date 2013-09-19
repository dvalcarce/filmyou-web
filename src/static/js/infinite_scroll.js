(function ($) {
    'use strict';

    $.fn.endlessPaginate = function(options) {
        var settings = {
            // Twitter-style pagination container selector.
            containerSelector: '#scrolling_container',
            loadingSelector: '#scrolling_loading',
            moreSelector: '#more_results',
            // If paginate-on-scroll is on, this margin will be used.
            magin : 20,
        }

        return this.each(function() {
            var element = $(this),
                loadedPages = 1;

            // Twitter-style pagination.
            element.on('click', settings.moreSelector, function() {
                var container = link.closest(settings.containerSelector),
                    loading = $(loadingSelector);
                // Avoid multiple Ajax calls.
                if (loading.is(':visible')) {
                    return false;
                }
                loading.show();
                var data = 'querystring_key=' + link.attr('rel').split(' ')[0];
                // Send the Ajax request.
                $.get(link.link.attr('href'), data, function(fragment) {
                    container.before(fragment);
                    container.remove();
                    // Increase the number of loaded pages.
                    loadedPages += 1;
                });
                return false;
            });

            // On scroll pagination.
            var win = $(window),
                doc = $(document);
            win.scroll(function(){
                if (doc.height() - win.height() - win.scrollTop()
                    <= settings.magin) {
                        element.find(settings.moreSelector).click();
                    }
                }
            });
        });
    };

    $.endlessPaginate = function(options) {
        return $('body').endlessPaginate(options);
    };

})(jQuery);
