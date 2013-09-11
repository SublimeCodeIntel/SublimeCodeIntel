"""
Safari/Webkit CSS extensions.
"""

import textwrap

### START: Auto generated

CSS_WEBKIT_DATA = {

    '-webkit-animation':
    {'description': 'Combines common animation properties into a single property.',
        'syntax': '-webkit-animation: name duration timing_function delay iteration_count direction [, ... ];',
        'values': {'delay': 'Defines when an animation starts.',
                  'direction': 'Determines whether the animation should play in reverse on alternate iterations.',
                  'duration': 'Specifies the length of time that an animation takes to complete one iteration.',
                  'iteration_count': 'Specifies the number of times an animation iterates.',
                  'name': 'The name of the animation.',
                  'timing_function': 'Defines how an animation progresses between keyframes.'},
        'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-animation-delay':
{'description': 'Defines when an animation starts.',
 'syntax': '-webkit-animation-delay: time [, ...];',
 'values': {'0': '(by default) ',
                  'now': 'The animation begins immediately. Available in iPhone OS 2.0 and later.'},
 'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-animation-direction':
{'description': 'Determines whether the animation should play in reverse on alternate iterations.',
 'syntax': '-webkit-animation-direction: direction [, ...]',
 'values': {'alternate': 'Play even-numbered iterations of the animation in the forward direction and odd-numbered iterations in the reverse direction. \n When an animation is played in reverse, the timing functions are also reversed. For example, when played in reverse, an ease-in animation appears as an ease-out animation.',
                          'normal': '(by default) Play each iteration of the animation in the forward direction.'},
 'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-animation-duration':
{'description': 'Specifies the length of time that an animation takes to complete one iteration.',
 'syntax': '-webkit-animation-duration: time [, ...]',
 'values': {'0': '(by default) ', '<time>': ''},
 'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-animation-iteration-count':
{'description': 'Specifies the number of times an animation iterates.',
 'syntax': '-webkit-animation-iteration-count: number [, ...]',
 'values': {'1': '(by default) ',
                  'infinite': 'Repeats the animation forever.'},
 'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-animation-name':
{'description': 'Specifies the name of an animation.',
 'syntax': '-webkit-animation-name: name [, ...]',
 'values': {'name': 'The name of the animation.'},
 'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-animation-play-state':
{'description': 'Determines whether the animation is running or paused.',
 'syntax': '-webkit-animation-play-state: play_state [, ...];',
 'values': {'paused': 'Pauses the animation.',
            'running': '(by default) Plays the animation.'},
 'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-animation-timing-function':
{'description': 'Defines how an animation progresses between keyframes.',
 'syntax': '-webkit-animation-timing-function: function [, ...]',
 'values': {'<function>': '',
            'ease': '(by default) Equivalent to  cubic-bezier(0.25, 0.1, 0.25, 1.0) .',
            'ease-in': 'Equivalent to  cubic-bezier(0.42, 0, 1.0, 1.0) .',
            'ease-in-out': 'Equivalent to  cubic-bezier(0.42, 0, 0.58, 1.0) .',
            'ease-out': 'Equivalent to  cubic-bezier(0, 0, 0.58, 1.0) .',
            'linear': 'Equivalent to  cubic-bezier(0.0, 0.0, 1.0, 1.0) .'},
 'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-appearance':
{'description': 'Changes the appearance of buttons and other controls to resemble native controls.',
 'syntax': '-webkit-appearance: appearance;',
 'values': {'button': '',
            'button-bevel': '',
            'caps-lock-indicator': 'The indicator that appears in a password field when Caps Lock is active. Available in Safari 4.0 and later. Available in iPhone OS 2.0 and later.',
            'caret': '',
            'checkbox': '',
            'default-button': '',
            'listbox': '',
            'listitem': '',
            'media-fullscreen-button': '',
            'media-mute-button': '',
            'media-play-button': '',
            'media-seek-back-button': '',
            'media-seek-forward-button': '',
            'media-slider': '',
            'media-sliderthumb': '',
            'menulist': '',
            'menulist-button': '',
            'menulist-text': '',
                          'menulist-textfield': '',
                          'none': '',
                          'push-button': '',
                          'radio': '',
                          'scrollbarbutton-down': 'Unsupported in Safari 4.0',
                          'scrollbarbutton-left': 'Unsupported in Safari 4.0',
                          'scrollbarbutton-right': 'Unsupported in Safari 4.0',
                          'scrollbarbutton-up': 'Unsupported in Safari 4.0',
                          'scrollbargripper-horizontal': 'Unsupported in Safari 4.0',
                          'scrollbargripper-vertical': 'Unsupported in Safari 4.0',
                          'scrollbarthumb-horizontal': 'Unsupported in Safari 4.0',
                          'scrollbarthumb-vertical': 'Unsupported in Safari 4.0',
                          'scrollbartrack-horizontal': 'Unsupported in Safari 4.0',
                          'scrollbartrack-vertical': 'Unsupported in Safari 4.0',
                          'searchfield': '',
                          'searchfield-cancel-button': '',
                          'searchfield-decoration': '',
                          'searchfield-results-button': '',
                          'searchfield-results-decoration': '',
                          'slider-horizontal': '',
                          'slider-vertical': '',
                          'sliderthumb-horizontal': '',
                          'sliderthumb-vertical': '',
                          'square-button': '',
                          'textarea': '',
                          'textfield': ''},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-backface-visibility':
{'description': 'Determines whether or not a transformed element is visible when it is not facing the screen.',
        'syntax': '-webkit-backface-visibility: visibility;',
        'values': {'hidden': 'The element is invisible if it is not facing the screen.',
                          'visible': '(by default) The element is always visible even when it is not facing the screen.'},
        'versions': ['iPhone OS 2.0']},

    '-webkit-background-clip':
{'description': 'Specifies the clipping behavior of the background of a box.',
        'syntax': '-webkit-background-clip: behavior;',
        'values': {'border': 'The background clips to the border of the box.',
                          'content': 'The background clips to the content of the box.',
                          'padding': 'The background clips to the padding of the box.',
                          'text': 'The background clips to the text of the box. Available in Safari 4.0 and later.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-background-composite':
{'description': 'Sets a compositing style for background images and colors.',
        'syntax': '-webkit-background-composite: compositing_style;',
        'values': {'border': '(by default) The background extends into the border area',
                          'padding': 'The background extends only into the padding area enclosed by the border'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-background-origin':
{'description': 'Determines where the  background-position  property is anchored.',
        'syntax': '-webkit-background-origin: origin;',
        'values': {'origin': 'The origin of the background position.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-background-size':
{'description': 'Overrides the size of a background image.',
        'syntax': '-webkit-background-size: length;',
        'values': {'length': 'The width and height of the background image.',
                          'length_x': 'The width of the background image.',
                          'length_y': 'The height of the background image.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-bottom-left-radius':
{'description': 'Specifies that the bottom-left corner of a box be rounded with the specified radius.',
        'syntax': '-webkit-border-bottom-left-radius: radius;',
        'values': {'horizontal_radius': 'The horizontal radius of the rounded corner.',
                          'radius': 'The radius of the rounded corner.',
                          'vertical_radius': 'The vertical radius of the rounded corner.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-bottom-right-radius':
{'description': 'Specifies that the bottom-right corner of a box be rounded with the specified radius.',
        'syntax': '-webkit-border-bottom-right-radius: radius;',
        'values': {'horizontal_radius': 'The horizontal radius of the rounded corner.',
                          'radius': 'The radius of the rounded corner.',
                          'vertical_radius': 'The vertical radius of the rounded corner.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-horizontal-spacing':
{'description': 'Defines the spacing between the horizontal portion of an element\u2019s border and the content within.',
        'syntax': '-webkit-border-horizontal-spacing: value;',
        'values': {'value': 'The amount of horizontal spacing.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-image':
{'description': 'Specifies an image as the border for a box.',
        'syntax': '-webkit-border-image: uri top right bottom left x_repeat y_repeat',
        'values': {'repeat': 'The image is tiled.',
                          'round': 'The image is stretched before it is tiled to prevent partial tiles.',
                          'stretch': 'The image is stretched to the size of the border.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-radius':
{'description': 'Specifies that the corners of a box be rounded with the specified radius.',
        'syntax': '-webkit-border-radius: radius;',
        'values': {'horizontal_radius': 'The horizontal radius of the rounded corners.',
                          'radius': 'The radius of the rounded corners.',
                          'vertical_radius': 'The vertical radius of the rounded corners.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-top-left-radius':
{'description': 'Specifies that the top-left corner of a box be rounded with the specified radius.',
        'syntax': '-webkit-border-top-left-radius: radius;',
        'values': {'horizontal_radius': 'The horizontal radius of the rounded corner.',
                          'radius': 'The radius of the rounded corner.',
                          'vertical_radius': 'The vertical radius of the rounded corner.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-top-right-radius':
{'description': 'Specifies that the top-right corner of a box be rounded with the specified radius.',
        'syntax': '-webkit-border-top-right-radius: radius;',
        'values': {'horizontal_radius': 'The horizontal radius of the rounded corner.',
                          'radius': 'The radius of the rounded corner.',
                          'vertical_radius': 'The vertical radius of the rounded corner.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-border-vertical-spacing':
{'description': 'Defines the spacing between the vertical portion of an element\u2019s border and the content within.',
        'syntax': '-webkit-border-vertical-spacing: value;',
        'values': {'value': 'The amount of vertical spacing.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-align':
{'description': 'Specifies the alignment of nested elements within an outer flexible box element.',
        'syntax': '-webkit-box-align: alignment;',
        'values': {'baseline': 'Elements are aligned with the baseline of the box.',
                          'center': 'Elements are aligned with the center of the box.',
                          'end': 'Elements are aligned with the end of the box.',
                          'start': 'Elements are aligned with the start of the box.',
                          'stretch': 'Elements are stretched to fill the box.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-direction':
{'description': 'Specifies the direction in which child elements of a flexible box element are laid out.',
        'syntax': '-webkit-box-direction: layout_direction;',
        'values': {'normal': '(by default) Elements are laid out in the default direction.',
                          'reverse': 'Elements are laid out in the reverse direction.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-flex':
{'description': 'Specifies an element\u2019s flexibility.',
        'syntax': '-webkit-box-flex: flex_value;',
        'values': {'<flexvalue>': 'Floating-point number'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-flex-group':
{'description': 'Specifies groups of dynamically resizing elements that are adjusted to be the same size.',
        'syntax': '-webkit-box-flex-group: group_number;',
        'values': {'<group_number>': 'Integer, nonnegative value'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-lines':
{'description': 'Specifies whether a flexible box should contain multiple lines of content.',
        'syntax': '-webkit-box-lines: behavior;',
        'values': {'multiple': 'The box can contain multiple lines of content.',
                          'single': 'The box can contain only one line of content.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-ordinal-group':
{'description': 'Specifies a rough ordering of elements in a flexible box.',
        'syntax': '-webkit-box-ordinal-group: group_number;',
        'values': {'<group_number>': 'Integer, nonnegative value'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-orient':
{'description': 'Specifies the layout of elements nested within a flexible box element.',
        'syntax': '-webkit-box-orient: orientation;',
        'values': {'block-axis': "Elements are oriented along the box's axis.",
                          'horizontal': 'Elements are oriented horizontally.',
                          'inline-axis': 'Elements are oriented along the inline axis.',
                          'vertical': 'Elements are oriented vertically.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-pack':
{'description': 'Specifies alignment of child elements within the current element in the direction of orientation.',
        'syntax': '-webkit-box-pack: alignment;',
        'values': {'center': 'Child elements are aligned to the center of the element.',
                          'end': 'Child elements are aligned to the end of the element.',
                          'justify': 'Child elements are justified with both the start and end of the element.',
                          'start': 'Child elements are aligned to the start of the element.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-box-reflect':
{'description': 'Defines a reflection of a border box.',
        'syntax': '-webkit-box-reflect: direction offset mask-box-image;',
        'values': {'above': 'The reflection appears above the border box.',
                          'below': 'The reflection appears below the border box.',
                          'left': 'The reflection appears to the left of the border box.',
                          'right': 'The reflection appears to the right of the border box.'},
        'versions': ['iPhone OS 2.0']},

    '-webkit-box-shadow':
{'description': 'Applies a drop shadow effect to the border box of an object.',
        'syntax': '-webkit-box-shadow: hoff voff blur color;',
        'values': {'none': '(by default) The box has no shadow.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-box-sizing':
{'description': 'Specifies that the size of a box be measured according to either its content (default) or its total size including borders.',
        'syntax': '-webkit-box-sizing: sizing_model;',
        'values': {'border-box': 'The box size includes borders in addition to content.',
                          'content-box': '(by default) The box size only includes content.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-column-break-after':
{'description': 'Determines whether a column break can and should occur after an element in a multicolumn flow layout.',
        'syntax': '-webkit-column-break-after: policy;',
        'values': {'always': 'A column break is always inserted after the element.',
                          'auto': '(by default) A right column break is inserted after the element where appropriate.',
                          'avoid': 'Column breaks are avoided after the element.',
                          'left': 'A left column break is inserted after the element.',
                          'right': 'A right column break is inserted after the element.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-break-before':
{'description': 'Determines whether a column break can and should occur before an element in a multicolumn flow layout.',
        'syntax': '-webkit-column-break-before: policy;',
        'values': {'always': 'A column break is always inserted before the element.',
                          'auto': '(by default) A right column break is inserted before the element where appropriate.',
                          'avoid': 'Column breaks are avoided before the element.',
                          'left': 'A left column break is inserted before the element.',
                          'right': 'A right column break is inserted before the element.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-break-inside':
{'description': 'Determines whether a column break should be avoided within the bounds of an element in a multicolumn flow layout.',
        'syntax': '-webkit-column-break-inside: policy;',
        'values': {'auto': '(by default) A right column break is inserted within the element where appropriate.',
                          'avoid': 'Column breaks are avoided within the element.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-count':
{'description': 'Specifies the number of columns desired in a multicolumn flow.',
        'syntax': '-webkit-column-count: number_of_columns;',
        'values': {'<number_of_columns>': 'Integer, nonnegative value',
                          'auto': '(by default) The element has one column.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-gap':
{'description': 'Specifies the space between columns in a multicolumn flow.',
        'syntax': '-webkit-column-gap: width;',
        'values': {'<width>': 'Length unit',
                          'normal': '(by default) Columns in the element have the normal gap width between them.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-rule':
{'description': 'Specifies the color, style, and width of the column rule.',
        'syntax': '-webkit-column-rule: width style color;',
        'values': {'color': 'The color of the column rule.',
                          'style': 'The style of the column rule.',
                          'width': 'The width of the column rule.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-rule-color':
{'description': 'Specifies the color of the column rule.',
        'syntax': '-webkit-column-rule-color: color;',
        'values': {'-webkit-activelink': 'The default color of a hyperlink that is being clicked.',
                          '-webkit-focus-ring-color': 'The color that surrounds a UI element, such as a text field, that has focus.',
                          '-webkit-link': 'The default color of a hyperlink that has been visited.',
                          '-webkit-text': 'The default text color.',
                          'activeborder': '',
                          'activecaption': '',
                          'appworkspace': '',
                          'aqua': '',
                          'background': '',
                          'black': '',
                          'blue': '',
                          'buttonface': '',
                          'buttonhighlight': '',
                          'buttonshadow': '',
                          'buttontext': '',
                          'captiontext': '',
                          'currentcolor': "(by default) The value of the element's color property.",
                          'fuchsia': '',
                          'gray': '',
                          'graytext': '',
                          'green': '',
                          'grey': '',
                          'highlight': '',
                          'highlighttext': '',
                          'inactiveborder': '',
                          'inactivecaption': '',
                          'inactivecaptiontext': '',
                          'infobackground': '',
                          'infotext': '',
                          'lime': '',
                          'maroon': '',
                          'match': '',
                          'menu': '',
                          'menutext': '',
                          'navy': '',
                          'olive': '',
                          'orange': '',
                          'purple': '',
                          'red': '',
                          'scrollbar': '',
                          'silver': '',
                          'teal': '',
                          'threeddarkshadow': '',
                          'threedface': '',
                          'threedhighlight': '',
                          'threedlightshadow': '',
                          'threedshadow': '',
                          'transparent': '',
                          'white': '',
                          'window': '',
                          'windowframe': '',
                          'windowtext': '',
                          'yellow': ''},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-rule-style':
{'description': 'Specifies the style of the column rule.',
        'syntax': '-webkit-column-rule-style: style;',
        'values': {'dashed': 'The column rule has a dashed line style.',
                          'dotted': 'The column rule has a dotted line style.',
                          'double': 'The column rule has a double solid line style.',
                          'groove': 'The column rule has a grooved style.',
                          'hidden': 'The column rule is hidden.',
                          'inset': 'The column rule has an inset style.',
                          'none': 'The column rule has no style.',
                          'outset': 'The column rule has an outset style.',
                          'ridge': 'The column rule has a ridged style.',
                          'solid': 'The column rule has a solid line style.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-rule-width':
{'description': 'Specifies the width of the column rule.',
        'syntax': '-webkit-column-rule-width: width;',
        'values': {'<width>': 'Length unit',
                          'medium': 'The column rule has a medium width.',
                          'thick': 'The column rule has a thick width.',
                          'thin': 'The column rule has a thin width.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-column-width':
{'description': 'Specifies the width of the column in a multicolumn flow.',
        'syntax': '-webkit-column-width: width;',
        'values': {'<width>': 'Length unit',
                          'auto': '(by default) Columns in the element are of normal width.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-columns':
{'description': 'A composite property that specifies the width and number of columns in a multicolumn flow layout.',
        'syntax': '-webkit-columns: width count;',
        'values': {'count': 'The number of columns.',
                          'width': 'The width of each column.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-dashboard-region':
{'description': 'Specifies the behavior of regions in a Dashboard widget.',
        'syntax': '-webkit-dashboard-region: dashboard-region(...) [...];',
        'values': {'none': 'No behavior is specified.'},
        'versions': ['Safari 3.0']},

    '-webkit-line-break':
{'description': 'Specifies line-breaking rules for CJK (Chinese, Japanese, and Korean) text.',
        'syntax': '-webkit-line-break: setting;',
        'values': {'after-white-space': 'The line breaks after white space.',
                          'normal': '(by default) A standard line-breaking rule.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-margin-bottom-collapse':
{'description': "Specifies the behavior of an element's bottom margin if it is adjacent to an element with a margin. Elements can maintain their respective margins or share a single margin between them.",
        'syntax': '-webkit-margin-bottom-collapse: collapse_behavior;',
        'values': {'collapse': 'Two adjacent margins are collapsed into a single margin.',
                          'discard': 'The element\u2019s margin is discarded if it is adjacent to another element with a margin.',
                          'separate': 'Two adjacent margins remain separate.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-margin-collapse':
{'description': 'Specifies the behavior of an element\u2019s vertical margins if it is adjacent to an element with a margin. Elements can maintain their respective margins or share a single margin between them.',
        'syntax': '-webkit-margin-collapse: collapse_behavior;',
        'values': {'collapse_behavior': 'The behavior of the vertical margins.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-margin-start':
{'description': 'Provides the width of the starting margin.',
        'syntax': '-webkit-margin-start: width;',
        'values': {'<width>': 'Number as a percentage, length unit',
                          'auto': '(by default) The margin is automatically determined.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-margin-top-collapse':
{'description': 'Specifies the behavior of an element\u2019s top margin if it is adjacent to an element with a margin. Elements can maintain their respective margins or share a single margin between them.',
        'syntax': '-webkit-margin-top-collapse: collapse_behavior;',
        'values': {'collapse': 'Two adjacent margins are collapsed into a single margin.',
                          'discard': 'The element\u2019s margin is discarded if it is adjacent to another element with a margin.',
                          'separate': 'Two adjacent margins remain separate.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-marquee':
{'description': 'Defines properties for showing content as though displayed on an electronic marquee sign.',
        'syntax': '-webkit-marquee: direction increment repetition style speed;',
        'values': {'direction': 'The direction of the marquee.',
                          'increment': 'The distance the marquee moves in each increment',
                          'repetition': 'The number of times the marquee repeats.',
                          'speed': 'The scroll or slide speed of the marquee.',
                          'style': 'The style of the marquee\u2019s motion.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-marquee-direction':
{'description': 'Specifies the direction of motion for a marquee box.',
        'syntax': '-webkit-marquee-direction: direction;',
        'values': {'ahead': 'The marquee moves from bottom to top.',
                          'auto': '(by default) The marquee moves in the default direction.',
                          'backwards': 'The marquee moves from right to left.',
                          'down': 'The marquee moves from bottom to top.',
                          'forwards': 'The marquee moves from left to right.',
                          'left': 'The marquee moves from right to left.',
                          'reverse': 'The marquee moves from top to bottom.',
                          'right': 'The marquee moves from left to right.',
                          'up': 'The marquee moves from bottom to top.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-marquee-increment':
{'description': 'Defines the distance the marquee moves in each increment.',
        'syntax': '-webkit-marquee-increment: distance;',
        'values': {'<distance>': 'Number as a percentage, length unit',
                          'large': 'The marquee moves a large amount in each increment.',
                          'medium': 'The marquee moves a medium amount in each increment.',
                          'small': 'The marquee moves a small amount in each increment.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-marquee-repetition':
{'description': 'Specifies the number of times a marquee box repeats (or  infinite ).',
        'syntax': '-webkit-marquee-repetition: iterations;',
        'values': {'<iterations>': 'Integer, nonnegative value',
                          'infinite': '(by default) The marquee repeats infinitely.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-marquee-speed':
{'description': 'Defines the scroll or slide speed of a marquee box.',
        'syntax': '-webkit-marquee-speed: speed;',
        'values': {'<distance>': 'Integer, nonnegative value',
                          '<time>': 'Time unit, nonnegative value',
                          'fast': 'The marquee moves at a fast speed.',
                          'normal': 'The marquee moves at a normal speed.',
                          'slow': 'The marquee moves at a slow speed.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-marquee-style':
{'description': 'Specifies the style of marquee motion.',
        'syntax': '-webkit-marquee-style: style;',
        'values': {'alternate': 'The marquee shifts back and forth.',
                          'none': 'The marquee does not move.',
                          'scroll': 'The marquee loops in its specified direction.',
                          'slide': 'The marquee moves in its specified direction, but stops either when the entirety of its content has been displayed or the content reaches the opposite border of its box, whichever comes second.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-mask':
{'description': 'Defines a variety of mask properties within one declaration.',
        'syntax': '-webkit-mask: attachment, clip, origin, image, repeat, composite, box-image;',
        'values': {'attachment': 'Defines the scrolling or fixed nature of the image mask. See  -webkit-mask-attachment .',
                          'clip': 'Specifies whether the mask should extend into the border of a box. See  -webkit-mask-clip .',
                          'composite': 'Sets a compositing style for a mask. See  -webkit-mask-composite .',
                          'image': 'Defines an image to be used as a mask for an element. See  -webkit-mask-image .',
                          'origin': 'Determines where the  -webkit-mask-position  property is anchored. See  -webkit-mask-origin .',
                          'repeat': 'Defines the repeating qualities of a mask. See  -webkit-mask-repeat .'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-attachment':
{'description': 'Defines the scrolling or fixed nature of the image mask.',
        'syntax': '-webkit-mask-attachment: mask_attachment;',
        'values': {'fixed': 'The mask does not move when the page scrolls.',
                          'scroll': 'The image moves when the page scrolls.'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-box-image':
{'description': 'Defines an image to be used as a mask for a border box.',
        'syntax': '-webkit-mask-box-image: uri top right bottom left x_repeat y_repeat;',
        'values': {'bottom': 'The distance from the bottom edge of the image.',
                          'left': 'The distance from the left edge of the image.',
                          'right': 'The distance from the right edge of the image.',
                          'top': 'The distance from the top edge of the image.',
                          'uri': 'The file path of the image.',
                          'x_repeat': 'The horizontal repeat style.',
                          'y_repeat': 'The vertical repeat style.'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-clip':
{'description': 'Specifies whether the mask should extend into the border of a box.',
        'syntax': '-webkit-mask-clip: behavior;',
        'values': {'behavior': 'The clipping behavior of the mask.'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-composite':
{'description': 'Sets a compositing style for a mask.',
        'syntax': '-webkit-mask-composite: compositing_style;',
        'values': {'border': '(by default) ', 'padding': ''},
        'versions': ['Safari 4.0']},

    '-webkit-mask-image':
{'description': 'Defines an image to be used as a mask for an element.',
        'syntax': '-webkit-mask-image: value;',
        'values': {'value': 'The file path of the image.'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-origin':
{'description': 'Determines where the -webkit-mask-position property is anchored.',
        'syntax': '-webkit-mask-origin: origin;',
        'values': {'border': "The mask's position is anchored at the upper-left corner of the element's border.",
                          'content': "The mask's position is anchored at the upper-left corner of the element's content.",
                          'padding': "The mask's position is anchored at the upper-left corner of the element's padding."},
        'versions': ['Safari 4.0']},

    '-webkit-mask-position':
{'description': 'Defines the position of a mask.',
        'syntax': '-webkit-mask-position: xpos;',
        'values': {'<position>': '',
                          'bottom': '',
                          'center': '',
                          'left': '',
                          'right': '',
                          'top': ''},
        'versions': ['Safari 4.0']},

    '-webkit-mask-position-x':
{'description': 'Defines the x-coordinate of the position of a mask.',
        'syntax': '-webkit-mask-position-x: value;',
        'values': {'value': 'The x-coordinate of the position of the mask.'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-position-y':
{'description': 'Defines the y-coordinate of the position of a mask.',
        'syntax': '-webkit-mask-position-y: value;',
        'values': {'value': 'The y-coordinate of the position of the mask.'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-repeat':
{'description': 'Defines the repeating qualities of a mask.',
        'syntax': '-webkit-mask-repeat: value;',
        'values': {'value': 'The repeating behavior of the mask.'},
        'versions': ['Safari 4.0']},

    '-webkit-mask-size':
{'description': 'Overrides the size of a mask.',
        'syntax': '-webkit-mask-size: length;',
        'values': {'length': 'The width and height of the mask.',
                          'length_x': 'The width of the mask.',
                          'length_y': 'The height of the mask.'},
        'versions': ['Safari 4.0']},

    '-webkit-nbsp-mode':
{'description': 'Defines the behavior of nonbreaking spaces within text.',
        'syntax': '-webkit-nbsp-mode: behavior;',
        'values': {'normal': 'Nonbreaking spaces are treated as usual.',
                          'space': 'Nonbreaking spaces are treated like standard spaces.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-padding-start':
{'description': 'Provides the width of the starting padding.',
        'syntax': '-webkit-padding-start: width;',
        'values': {'<length>': '', '<percentage>': ''},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-perspective':
{'description': 'Gives depth to a scene, causing elements farther away from the viewer to appear smaller.',
        'syntax': '-webkit-perspective: value;',
        'values': {'<distance>': 'Length in pixel',
                          'none': '(by default) No perspective transform is applied.'},
        'versions': ['iPhone OS 2.0']},

    '-webkit-perspective-origin':
{'description': 'Sets the origin of the  -webkit-perspective  property described in  "-webkit-perspective."',
        'syntax': '-webkit-perspective-origin: posx posy;',
        'values': {'50%': '50% (by default) ',
                          '<percentage>': '',
                          'bottom': 'Sets the y-origin to the bottom of the element\u2019s border box.',
                          'center': 'Sets the x or y origin to the center of the element\u2019s border box. If this constant appears before  left  or  right , specifies the y-origin. If it appears after  top  or  bottom , specifies the x-origin. If appears alone, centers both the x and y origin.',
                          'left': 'Sets the x-origin to the left side of the border box.',
                          'right': 'Sets the x-origin to the right side of the border box.',
                          'top': 'Sets the y-origin to the top of the element\u2019s border box.'},
        'versions': ['iPhone OS 2.0']},

    '-webkit-rtl-ordering':
{'description': 'Overrides ordering defaults for right-to-left content.',
        'syntax': '-webkit-rtl-ordering: order;',
        'values': {'logical': 'Raw content is in mixed order (requiring a bidirectional renderer).',
                          'visual': 'Right-to-left content is encoded in reverse order so an entire line of text can be rendered from left to right in a unidirectional fashion.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-tap-highlight-color':
{'description': 'Overrides the highlight color shown when the user taps a link or a JavaScript clickable element in Safari on iPhone.',
        'syntax': '-webkit-tap-highlight-color: color;',
        'values': {'color': 'The tapped link color.'},
        'versions': ['iPhone OS 1.1.1']},

    '-webkit-text-fill-color':
{'description': 'Specifies a fill color for text.',
        'syntax': '-webkit-text-fill-color: color;',
        'values': {'-webkit-activelink': 'The default color of a hyperlink that is being clicked.',
                          '-webkit-focus-ring-color': 'The color that surrounds a UI element, such as a text field, that has focus.',
                          '-webkit-link': 'The default color of a hyperlink that has been visited.',
                          '-webkit-text': 'The default text color.',
                          'activeborder': '',
                          'activecaption': '',
                          'appworkspace': '',
                          'aqua': '',
                          'background': '',
                          'black': '',
                          'blue': '',
                          'buttonface': '',
                          'buttonhighlight': '',
                          'buttonshadow': '',
                          'buttontext': '',
                          'captiontext': '',
                          'currentcolor': '(by default) The value of the element\u2019s color property.',
                          'fuchsia': '',
                          'gray': '',
                          'graytext': '',
                          'green': '',
                          'grey': '',
                          'highlight': '',
                          'highlighttext': '',
                          'inactiveborder': '',
                          'inactivecaption': '',
                          'inactivecaptiontext': '',
                          'infobackground': '',
                          'infotext': '',
                          'lime': '',
                          'maroon': '',
                          'match': '',
                          'menu': '',
                          'menutext': '',
                          'navy': '',
                          'olive': '',
                          'orange': '',
                          'purple': '',
                          'red': '',
                          'scrollbar': '',
                          'silver': '',
                          'teal': '',
                          'threeddarkshadow': '',
                          'threedface': '',
                          'threedhighlight': '',
                          'threedlightshadow': '',
                          'threedshadow': '',
                          'transparent': '',
                          'white': '',
                          'window': '',
                          'windowframe': '',
                          'windowtext': '',
                          'yellow': ''},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-text-security':
{'description': 'Specifies the shape to use in place of letters in a password input field.',
        'syntax': '-webkit-text-security: shape;',
        'values': {'circle': 'A circle shape.',
                          'disc': 'A disc shape.',
                          'none': 'No shape is used.',
                          'square': 'A square shape.'},
        'versions': ['Safari 3.0', 'iPhone OS 1.0']},

    '-webkit-text-size-adjust':
{'description': 'Specifies a size adjustment for displaying text content in Safari on iPhone.',
        'syntax': '-webkit-text-size-adjust: percentage;',
        'values': {'<percentage>': 'The size in percentage at which to display text in Safari on iPhone.',
                          'auto': 'The text size is automatically adjusted for Safari on iPhone.',
                          'none': '(by default) The text size is not adjusted.'},
        'versions': ['iPhone OS 1.0']},

    '-webkit-text-stroke':
{'description': 'Specifies the width and color of the outline (stroke) of text.',
        'syntax': '-webkit-text-stroke: width color;',
        'values': {'color': 'The color of the stroke.',
                          'width': 'The width of the stroke.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-text-stroke-color':
{'description': 'Specifies the color of the outline (stroke) of text.',
        'syntax': '-webkit-text-stroke-color: color;',
        'values': {'-webkit-activelink': 'The default color of a hyperlink that is being clicked.',
                          '-webkit-focus-ring-color': 'The color that surrounds a UI element, such as a text field, that has focus.',
                          '-webkit-link': 'The default color of a hyperlink that has been visited.',
                          '-webkit-text': 'The default text color.',
                          'activeborder': '',
                          'activecaption': '',
                          'appworkspace': '',
                          'aqua': '',
                          'background': '',
                          'black': '',
                          'blue': '',
                          'buttonface': '',
                          'buttonhighlight': '',
                          'buttonshadow': '',
                          'buttontext': '',
                          'captiontext': '',
                          'currentcolor': "(by default) The value of the element's color property.",
                          'fuchsia': '',
                          'gray': '',
                          'graytext': '',
                          'green': '',
                          'grey': '',
                          'highlight': '',
                          'highlighttext': '',
                          'inactiveborder': '',
                          'inactivecaption': '',
                          'inactivecaptiontext': '',
                          'infobackground': '',
                          'infotext': '',
                          'lime': '',
                          'maroon': '',
                          'match': '',
                          'menu': '',
                          'menutext': '',
                          'navy': '',
                          'olive': '',
                          'orange': '',
                          'purple': '',
                          'red': '',
                          'scrollbar': '',
                          'silver': '',
                          'teal': '',
                          'threeddarkshadow': '',
                          'threedface': '',
                          'threedhighlight': '',
                          'threedlightshadow': '',
                          'threedshadow': '',
                          'transparent': '',
                          'white': '',
                          'window': '',
                          'windowframe': '',
                          'windowtext': '',
                          'yellow': ''},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-text-stroke-width':
{'description': 'Specifies the width for the text outline.',
        'syntax': '-webkit-text-stroke-width: width;',
        'values': {'<width>': 'Length unit',
                          'medium': 'A medium stroke.',
                          'thick': 'A thick stroke.',
                          'thin': 'A thin stroke.'},
        'versions': ['Safari 3.0', 'iPhone OS 2.0']},

    '-webkit-touch-callout':
{'description': 'Disables the default callout shown when you touch and hold a touch target.',
        'syntax': '-webkit-touch-callout: behavior;',
        'values': {'inherit': '', 'none': ''},
        'versions': ['iPhone OS 2.0']},

    '-webkit-transform':
{'description': 'Specifies transformations to be applied to an element.',
        'syntax': '-webkit-transform: function ... ;',
        'values': {'<function>': '',
                          'none': '(by default) No transforms are applied.'},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-transform-origin':
{'description': 'Sets the origin for the  -webkit-transform  property.',
        'syntax': '-webkit-transform-origin: posx;',
        'values': {'50%': '50% (by default) ',
                          'bottom': '',
                          'center': '',
                          'left': '',
                          'right': '',
                          'top': ''},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-transform-origin-x':
{'description': 'The x coordinate of the origin for transforms applied to an element with respect to its border box.',
        'syntax': '-webkit-transform-origin-x: posx;',
        'values': {'posx': 'The x origin as a percentage or value.'},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-transform-origin-y':
{'description': 'The y coordinate of the origin for transforms applied to an element with respect to its border box.',
        'syntax': '-webkit-transform-origin-y: posy;',
        'values': {'posy': 'The y origin as a percentage or value.'},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-transform-origin-z':
{'description': 'The z coordinate of the origin for transforms applied to an element with respect to its border box.',
        'syntax': '-webkit-transform-origin-z: posz;',
        'values': {'posz': 'The z origin as a percentage or value.'},
        'versions': ['iPhone OS 2.0']},

    '-webkit-transform-style':
{'description': 'Defines how nested, transformed elements are rendered in 3D space.',
        'syntax': '-webkit-transform-style: style;',
        'values': {'flat': '(by default) Flatten all children of this element into the 2D plane.',
                          'preserve-3d': 'Preserve the 3D perspective.'},
        'versions': ['iPhone OS 2.0']},

    '-webkit-transition':
{'description': 'Combines  -webkit-transition-delay ,  -webkit-transition-duration ,  -webkit-transition-property , and  -webkit-transition-timing-function  into a single property.',
        'syntax': '-webkit-transition: property duration timing_function delay [, ...];',
        'values': {'delay': 'Defines when the transition starts. See  -webkit-transition-delay .',
                          'duration': 'Defines how long the transition from the old value to the new value should take. See  -webkit-transition-duration .',
                          'property': 'Specifies the name of the CSS property to which the transition is applied. See  -webkit-transition-property .',
                          'timing_function': 'Specifies how the intermediate values used during a transition are calculated. See  -webkit-transition-timing-function .'},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-transition-delay':
{'description': 'Defines when the transition starts.',
        'syntax': '-webkit-transition-delay: time [, ...];',
        'values': {'0': '(by default) ',
                          'now': 'The transition begins immediately. Available in iPhone OS 2.0 and later.'},
        'versions': ['Safari 4.0', 'iPhone OS 2.0']},

    '-webkit-transition-duration':
{'description': 'Defines how long the transition from the old value to the new value should take.',
        'syntax': '-webkit-transition-duration: time [, ...];',
        'values': {'0': '(by default) '},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-transition-property':
{'description': 'Specifies the name of the CSS property to which the transition is applied.',
        'syntax': '-webkit-transition-property: name;',
        'values': {'<name>': 'CSS property name',
                          'all': '(by default) The default transition name.',
                          'none': 'No transition specified.'},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-transition-timing-function':
{'description': 'Specifies how the intermediate values used during a transition are calculated.',
        'syntax': '-webkit-transition-timing-function: timing_function [, ...];',
        'values': {'<timing_function>': '',
                          'ease': '(by default) Equivalent to  cubic-bezier(0.25, 0.1, 0.25, 1.0)',
                          'ease-in': 'Equivalent to  cubic-bezier(0.42, 0, 1.0, 1.0)',
                          'ease-in-out': 'Equivalent to  cubic-bezier(0.42, 0, 0.58, 1.0)',
                          'ease-out': 'Equivalent to  cubic-bezier(0, 0, 0.58, 1.0)',
                          'linear': 'Equivalent to  cubic-bezier(0.0, 0.0, 1.0, 1.0)'},
        'versions': ['Safari 3.1', 'iPhone OS 2.0']},

    '-webkit-user-drag':
{'description': 'Specifies that an entire element should be draggable instead of its contents.',
        'syntax': '-webkit-user-drag: behavior;',
        'values': {'auto': '(by default) The default dragging behavior is used.',
                          'element': 'The entire element is draggable instead of its contents.',
                          'none': 'The element cannot be dragged at all.'},
        'versions': ['Safari 3.0']},

    '-webkit-user-modify':
{'description': 'Determines whether a user can edit the content of an element.',
        'syntax': '-webkit-user-modify: policy;',
        'values': {'read-only': 'The content is read-only.',
                          'read-write': 'The content can be read and written.',
                          'read-write-plaintext-only': 'The content can be read and written, but any rich formatting of pasted text is lost.'},
        'versions': ['Safari 3.0']},

    '-webkit-user-select':
{'description': 'Determines whether a user can select the content of an element.',
        'syntax': '-webkit-user-select: policy;',
        'values': {'auto': '(by default) The user can select content in the element.',
                          'none': 'The user cannot select any content.',
                          'text': 'The user can select text in the element.'},
        'versions': ['Safari 3.0', 'iPhone OS 3.0']},
}


### END: Auto generated


CSS_WEBKIT_SPECIFIC_ATTRS_DICT = {}
CSS_WEBKIT_SPECIFIC_CALLTIP_DICT = {}
for attr, details in list(CSS_WEBKIT_DATA.items()):
    values = details.get("values", {})
    versions = details.get("versions", [])
    attr_completions = sorted(values.keys())
    if attr_completions:
        CSS_WEBKIT_SPECIFIC_ATTRS_DICT[attr] = attr_completions
    else:
        CSS_WEBKIT_SPECIFIC_ATTRS_DICT[attr] = None
    description = details.get("description", '')
    if versions:
        description += "\nVersions: %s\n" % (", ".join(versions))
    if description:
        desc_lines = textwrap.wrap(description, width=60)
        if values:
            desc_lines.append("")
            for value, attr_desc in list(values.items()):
                attr_desc = "  %r: %s" % (value, attr_desc)
                attr_desc_lines = textwrap.wrap(attr_desc, width=50)
                for i in range(len(attr_desc_lines)):
                    attr_line = attr_desc_lines[i]
                    if i > 0:
                        attr_line = "        " + attr_line
                    desc_lines.append(attr_line)
        CSS_WEBKIT_SPECIFIC_CALLTIP_DICT[attr] = "\n".join(
            desc_lines).encode("ascii", 'replace')
