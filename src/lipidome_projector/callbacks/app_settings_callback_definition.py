from dash import callback, Output, Input, State

from lipidome_projector.front_end.front_end_coordination import FrontEnd


def reg_app_settings_callbacks_python(fe: FrontEnd) -> None:
    @callback(
        Output(fe.about_modal.element_id, "is_open"),
        Input(fe.about_button.element_id, "n_clicks"),
        State(fe.about_modal.element_id, "is_open"),
        prevent_initial_call=True,
    )
    def toggle_about_modal(
        open_about_modal: int | None, is_open: bool
    ) -> bool:
        return not is_open
