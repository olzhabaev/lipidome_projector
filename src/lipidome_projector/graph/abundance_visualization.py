"""Module concerning plotly based abundance visulizations."""

import logging

from dash_bootstrap_templates import load_figure_template

import plotly.express as px

from plotly.graph_objects import Figure

from lipid_data_processing.lipidomes.lipid_abundances import LipidAbundances


logger: logging.Logger = logging.getLogger(__name__)


def generate_lipid_abundance_bar_chart(
    lipid_abundances: LipidAbundances,
    sample_colormap: dict[str, str] | None = None,
    template: str = "plotly",
) -> Figure:
    """Generate lipidome abundance bar chart.
    :param lipid_abundances: Lipid abundances.
    :param sample_colormap: Colormap for samples.
    :param template: Plotly template.
    :returns: Lipidome abundance bar chart.
    """

    load_figure_template(template)

    figure: Figure = px.bar(
        lipid_abundances.abundance_df,
        x=lipid_abundances.sample_column_name,
        y=lipid_abundances.abundance_column_name,
        color=lipid_abundances.sample_column_name,
        color_discrete_map=sample_colormap,
        template=template,
    )

    figure.update_layout(showlegend=False)

    return figure


def generate_lipid_abundance_pie_chart(
    lipid_abundances: LipidAbundances,
    sample_colormap: dict[str, str] | None = None,
) -> Figure:
    """Generate lipidome abundance pie chart.
    :param lipid_abundances: Lipid abundances.
    :param sample_colormap: Colormap for samples.
    :returns: Lipidome abundance pie chart.
    """
    figure: Figure = px.pie(
        lipid_abundances.abundance_df,
        names=lipid_abundances.sample_column_name,
        values=lipid_abundances.abundance_column_name,
        color=lipid_abundances.sample_column_name,
        color_discrete_map=sample_colormap,
    )

    return figure
