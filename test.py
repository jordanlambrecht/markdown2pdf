from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Frame, RadioList
from prompt_toolkit.layout.containers import Window, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

# Define styles
style = Style.from_dict({
    'dialog.title': 'bg:ansiblue fg:ansiwhite',
})

# Define keybindings
kb = KeyBindings()

@kb.add('c-c')
@kb.add('c-q')
def exit_(event):
    event.app.exit()

# Welcome message and ASCII art placeholder
welcome_message = "Your ASCII art and welcome message goes here..."

def main():
    radio_list = RadioList(
        values=[
            ('Traefik Documentation', 'traefik'),
            ('Create a new project', 'new'),
        ],
    )

    def get_selected():
        return radio_list.current_value

    # Frame for the radio list
    radio_frame = Frame(
        title="[Project Selection]",
        body=Window(content=radio_list)
    )

    # Create a layout with the ASCII art and welcome message at the top
    # and the radio list in the middle
    root_container = Window(content=FormattedTextControl(welcome_message))
    dialog = Frame(
        title="Dialog Title",
        body=radio_frame
    )
    layout = Layout(root_container)

    # Create an application instance
    app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)

    app.run()

    # After the application has finished running, you can retrieve the selected value
    selected_option = get_selected()
    print(f"Selected option: {selected_option}")

if __name__ == '__main__':
    main()
