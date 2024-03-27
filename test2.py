#!/usr/bin/env python
"""
"""
from pygments.lexers.html import HtmlLexer
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import Float, HSplit, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.dimension import Dimension

from prompt_toolkit.layout import Float, FloatContainer, HSplit, Layout
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.layout import Float, FloatContainer, Layout, Window
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    Box,
    Button,
    Dialog,
    Frame,
    Label,
    RadioList,
    TextArea,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Frame
# ASCII art for the welcome message
ascii_art = r"""
      ██            ██                        
    ██░░██        ██░░██                      
    ██░░▒▒████████▒▒░░██                ████  
  ██▒▒░░░░▒▒▒▒░░▒▒░░░░▒▒██            ██░░░░██
  ██░░░░░░░░░░░░░░░░░░░░██            ██  ░░██
██▒▒░░░░░░░░░░░░░░░░░░░░▒▒████████      ██▒▒██
██░░  ██  ░░██░░  ██  ░░  ▒▒  ▒▒  ██    ██░░██
██░░░░░░░░██░░██░░░░░░░░░░▒▒░░▒▒░░░░██████▒▒██
██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██░░██  
██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██░░██  
██░░░░░░░░░░░ Markdown2PDF ░░░░░░░░░░░░░██    
██▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██    
██▒▒░░░░░░░░░░░░░ Jordan Lambrecht ░░░░░░██    
██▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒██    
  ██▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒██      
    ██▒▒░░▒▒▒▒░░▒▒░░░░░░▒▒░░▒▒▒▒░░▒▒██        
      ██░░████░░██████████░░████░░██          
      ██▓▓░░  ▓▓██░░  ░░██▓▓  ░░▓▓██          
"""
def get_half_terminal_width():
    app = get_app()  # Make sure to import get_app from prompt_toolkit.application.current
    if app.is_running:
        width = app.output.get_size().columns
        # Use Dimension constructor for exact values correctly
        return Dimension.exact(width // 2)
    else:
        # Return a Dimension object with an exact size without using 'exact' as a keyword argument
        return Dimension.exact(80)
    
class CustomRadioList(RadioList):
    def _get_text_fragments(self):
        # Custom emojis or characters for radio buttons
        selected_indicator = '[ 👍 ]'  # Example: Emoji for selected item
        unselected_indicator = '[    ]'  # Example: Emoji for unselected item

        def get_line(i):
            if i == self._selected_index:
                indicator = selected_indicator
            else:
                indicator = unselected_indicator
            return [
                ('', ' '),
                ('class:radio-selected' if i == self._selected_index else 'class:radio-unselected', indicator),
                ('', ' '),
                ('class:radio', self.values[i][0]),
                ('', '\n'),
            ]

        return [item for i in range(len(self.values)) for item in get_line(i)]
 

# Global key bindings.
bindings = KeyBindings()
bindings.add("tab")(focus_next)
bindings.add("s-tab")(focus_previous)
@bindings.add("c-c", eager=True)
@bindings.add("c-q", eager=True)
@bindings.add("escape", eager=True)
def _(event):
    event.app.exit()
def accept_yes():
    get_app().exit(result=True)


def accept_no():
    get_app().exit(result=False)


def do_exit():
    get_app().exit(result=False)
from prompt_toolkit.styles import Style

style = Style.from_dict({
    # General background and foreground colors
    'bg': 'bg:#282a36 #f8f8f2',  # Dark grey background with soft white text
    
    # Dialog and frame styles
    'dialog': 'bg:#44475a #f8f8f2',  # Dialog background with light text
    'dialog.title': 'bg:#6272a4 #f8f8f2 bold',  # Dialog title
    'dialog.body': 'bg:#44475a #f8f8f2',  # Dialog body
    'frame.bg': 'bg:#282a36',  # Main frame background
    'frame.top': 'bg:#6272a4 #f8f8f2',  # Top frame with a distinct color
    'frame.border': 'bg:#44475a',  # Frame border
    
    # Button styles
    'button': 'bg:#50fa7b #282a36',  # Green button with dark text
    'button.focused': 'bg:#f1fa8c #282a36 bold',  # Focused button with yellow background
    
    # Radio list styles
    'radiolist': 'bg:#44475a #f8f8f2',  # Radio list
    'radiolist focused': 'bg:#f1fa8c #282a36 bold',  # Focused radio item
    
    # Text area styles
    'text-area': 'bg:#44475a #f8f8f2',  # Text area
    
    # Label styles
    'label': 'bg:#282a36 #f8f8f2',  # Label
    
    # Shadow for floating elements
    'shadow': 'bg:#000000',  # Shadow effect
    
    # Custom class for highlighting important text
    'highlight': 'bg:#282a36 #ff79c6',  # Pinkish text for highlights
    
    # Error and warning styles
    'error': 'bg:#ff5555 #f8f8f2',  # Error messages with red background
    'warning': 'bg:#ffb86c #282a36',  # Warning messages with orange background
})

yes_button = Button(text="Yes", handler=accept_yes)
no_button = Button(text="No", handler=accept_no)

textfield = TextArea(lexer=PygmentsLexer(HtmlLexer))

radios = CustomRadioList(
    values=[
        ("Red", "red"),
        ("Green", "green"),
        ("Blue", "blue"),
        ("Orange", "orange"),
        ("Yellow", "yellow"),
        ("Purple", "Purple"),
        ("Brown", "Brown"),
    ]
)

dialog = Dialog(
    title="Floating Dialog",
    body=radios,
    buttons=[yes_button, no_button],
    with_background=True
)

top_frame = VSplit(
    [
        Frame(body=Label(text="Left frame\ncontent"), style="class:frame.top"),
        Frame(body=Label(text="Right frame\ncontent"),  style="class:frame.top"),
    ],
    height=D.exact(6),
)
main_frame = Frame(
    body=FloatContainer(
        content=Window(content=FormattedTextControl(text="Main content here..."), style="class:frame.bg"),
        floats=[
            Float(content=HSplit([dialog, Frame(body=TextArea( text=ascii_art, lexer=PygmentsLexer(HtmlLexer)), style="class:frame.bg")], align="CENTER", width=get_half_terminal_width())),
        ]
    ),
    style="class:frame.bg"
)

# VSplit to contain the dialog and the text area
# centered_content = VSplit([dialog, text_area], align="CENTER")

# textfield = TextArea(lexer=PygmentsLexer(HtmlLexer))
# info_label = Label(text= TITLE)    
# main_inner_body = VSplit([dialog, radios])
root_container = HSplit([top_frame, main_frame], padding=0)



def display_welcome():
    print(f"----------------------------------------------------------")
    print("        ")
    print("        ")
    print(style.CYAN + ascii_art + style.RESET)
    print("        ")
    print(f"{style.CYAN}Welcome to the Markdown to PDF Converter. Because why not?{style.RESET}")
    print(f"{style.YELLOW}We're transforming your Markdown files into PDFs, as if the world needed more PDFs...{style.RESET}")

def display_goodbye():
    print(f"\n{style.CYAN}----------------------------------------------------------{style.RESET}")
    print(f"\n{style.CYAN}  Program completed successfully. Have a blessed day! 👋  {style.RESET}")
    print(f"\n{style.CYAN}----------------------------------------------------------{style.RESET}")
  




application = Application(
    # layout=Layout(root_container, focused_element=yes_button, ),
    layout=Layout(root_container),
    key_bindings=bindings,
    style=style,
    mouse_support=True,
    full_screen=True,
)


def run():
    result = application.run()
    print("You said: %r" % result)


if __name__ == "__main__":
    run()