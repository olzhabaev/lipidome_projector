var currentTooltip = null;  // Variable to keep track of the current tooltip

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        trunc_legend_and_add_tooltip: function(figure, id) {
            var legendItems = document.querySelectorAll(`div#${id} .legendtext`);
            legendItems.forEach(function (legend_entry, index) {

                // Retrieve the customdata to get the untruncated trace name
                var adjustedIndex = index - 1;
                var untruncated_color_group_class = '';
                if (figure.data[adjustedIndex] !== undefined && figure.data[adjustedIndex].customdata !== undefined) {
                    untruncated_color_group_class = figure.data[adjustedIndex].customdata;
                }
                // Check if the item's text was truncated
                if (legend_entry.textContent.includes('...')) {

                    legend_entry.addEventListener('mouseover', function (event) {
                        // If there's a tooltip currently displayed, remove it
                        if (currentTooltip) {
                            currentTooltip.remove();
                        }

                        // Add a tooltip with the untruncated name
                        var tooltip = document.createElement('div');
                        tooltip.className = 'legend-tooltip';
                        tooltip.textContent = untruncated_color_group_class;
                        document.body.appendChild(tooltip);

                        // Tooltip placement
                        var rect = this.getBoundingClientRect();
                        var xPosition = rect.right;
                        var yPosition = window.pageYOffset + rect.top - tooltip.offsetHeight;
                        if (xPosition + tooltip.offsetWidth > window.innerWidth) {
                            xPosition = rect.left - tooltip.offsetWidth;
                        }
                        tooltip.style.left = xPosition + 'px';
                        tooltip.style.top = yPosition + 'px';
                        tooltip.style.opacity = 1;

                        // Update the current tooltip
                        currentTooltip = tooltip;

                        // Remove the tooltip after 1 second
                        setTimeout(function() {
                            tooltip.remove();
                            // If the tooltip being removed is the current tooltip, set currentTooltip to null
                            if (tooltip === currentTooltip) {
                                currentTooltip = null;
                            }
                        }, 1000);
                    });
                }
            });
            return window.dash_clientside.no_update
        },

        invert_structure_image_bg_on_dark_theme: function(img, theme_name, id) {

            const imgElement = document.getElementById(id);
            if (imgElement !== null) {
               const darkThemes = ['cyborg', 'darkly', 'slate', 'solar', 'superhero', 'vapor'];
               const isDarkTheme = darkThemes.some(darkTheme => theme_name.includes(darkTheme));
               imgElement.style.filter = isDarkTheme ? 'invert(1)' : 'none';
            }
            return window.dash_clientside.no_update;

        },

        update_figure_config: function(file_name, file_type, file_width, file_height, file_scaling_factor, figure) {
            fig = JSON.parse(JSON.stringify(figure))
            config={
                "toImageButtonOptions": {
                    "format": file_type,
                    "filename": file_name,
                    "width": file_width,
                    "height": file_height,
                    "scale": file_scaling_factor
                }
            }
            return [fig, config]
        },

        tour_listens_to_keys: function(popover_is_open, next_button_id, close_button_id) {
            if (popover_is_open) {
                document.addEventListener('keydown', function(event) {
                    if (event.key === 'ArrowRight') {
                        const nextButton = document.getElementById(next_button_id);
                        if (nextButton) {
                            nextButton.click();
                        }
                    }
                    else if (event.key === 'Escape') {
                        const closeButton = document.getElementById(close_button_id);
                        if (closeButton) {
                            closeButton.click();
                        }
                    }
                });
            }
            else {
                document.removeEventListener('keydown', function(event){});
            }
            return window.dash_clientside.no_update;
        },

        updateButtonColor: function(button_click, button_id) {
        let intervalId;
        const button = document.getElementById(button_id);
        const checkSpinnerAndAdjustColor = () => {
            const nextSibling = button.nextElementSibling;
            const spinner = nextSibling.querySelector('.dash-default-spinner');
            if (spinner) {
                button.style.color = 'var(--bs-btn-bg)';
            } else {
                button.style.color = 'var(--bs-btn-color)';
                clearInterval(intervalId);
            }
        };
        checkSpinnerAndAdjustColor();
        intervalId = setInterval(checkSpinnerAndAdjustColor, 100);
        return window.dash_clientside.no_update;
    }

    }
});