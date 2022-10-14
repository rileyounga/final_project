import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import plotly.express as px
import panel as pn
import holoviews as hv

pn.extension()
import hvplot.pandas


def scatter_reg(df):
    df = df[['Sales', 'Profit', 'Category']]
    # take only the 95th percentile of sales
    df = df[df['Sales'] < df['Sales'].quantile(0.95)]
    fig = px.scatter(df, x='Sales', y='Profit', symbol='Category', hover_name='Category', trendline='ols',
                     trendline_color_override='#4b0a17', height=500, color_discrete_sequence=['#1b2252'], opacity=0.5)
    fig.update_layout(title='Sales vs Profit with Regression Line')
    fig.update_yaxes(title_text='Profit (USD)', tickprefix="$")
    fig.update_xaxes(title_text='Sales (USD)', tickprefix="$")
    return fig


def choropleth(df):
    df = df[['Country', 'Profit']]
    df = df.groupby(['Country']).agg({'Profit': 'sum'}).reset_index()
    fig = px.choropleth(df, locations='Country', locationmode='country names', color='Profit', hover_name='Country',
                        color_continuous_scale='balance', color_continuous_midpoint=0, height=500, width=800)
    fig.update_layout(title_text='Total Profit by Country')
    return fig


def main():
    df = pd.read_csv('superstore_dataset2011-2015.csv', encoding='unicode_escape', infer_datetime_format=True)
    df['Year'] = pd.DatetimeIndex(df['Order Date']).year
    df['Month'] = pd.DatetimeIndex(df['Order Date']).month
    idf = df.interactive()
    # Create widgets
    year_slider = pn.widgets.IntSlider(name='Year', start=2011, end=2014, value=2011)
    category_select = pn.widgets.CheckButtonGroup(name='Category',
                                                  options=['Furniture', 'Office Supplies', 'Technology'],
                                                  value=['Furniture'])
    # Create a choropleth map of total sales by country
    map_plot = choropleth(df)
    # Create a bar chart of total sales by sub-category filter by category, highlight
    # the sub-category with the highest sales
    bar_pipeline = (idf[(idf.Year == year_slider) & (idf.Category.isin(category_select))]
                    .groupby(['Sub-Category'])
                    .agg({'Sales': 'sum'})
                    .reset_index()
                    .sort_values('Sales', ascending=False))
    bar_chart = bar_pipeline.hvplot(kind='bar', x='Sub-Category', y='Sales', rot=75, yformatter="$%.0f",
                                    title='Total Sales by Sub-Category', c='#1b2252', ylabel='Sales (USD)')
    max_pipeline = (bar_pipeline[bar_pipeline.Sales == bar_pipeline.Sales.max()])
    bar_chart *= max_pipeline.hvplot(kind='bar', x='Sub-Category', y='Sales', rot=75, yformatter="$%.0f",
                            title='Total Sales by Sub-Category', c='#4b0a17', ylabel='Sales (USD)')

    # Create a line plot of total sales by month
    line_pipeline = (idf[(idf.Year == year_slider) & (idf.Category.isin(category_select))]
                     .groupby(['Month'])
                     .agg({'Sales': 'sum'})
                     .reset_index())
    sales_plot = line_pipeline.hvplot(kind='line', x='Month', y='Sales', yformatter="$%.0f",
                                      title='Total Sales by Month', c='#1b2252', ylabel='Sales (USD)')

    # Create a scatter plot of Sales vs Profit with a regression line
    scatter_pipeline = (idf[(idf.Category.isin(category_select)) &
                            (idf['Sales'] < idf['Sales'].quantile(0.95))])
    scatter_plot = scatter_pipeline.hvplot.scatter(x='Sales', y='Profit', title='Sales vs Profit',
                                                   c='#1b2252', yformatter="$%.0f", hover=False, height=500,
                                                   xlabel='Sales (USD)', ylabel='Profit (USD)')
    reg_plt = scatter_reg(df)

    template = pn.template.FastListTemplate(
        title='Superstore Data Visualization',
        sidebar=[pn.pane.Markdown('## Superstore Data Visualization'), year_slider,
                 category_select],
        main=[pn.Row(sales_plot.panel(), bar_chart.panel()), pn.Row(scatter_plot.panel(), reg_plt),
              pn.Row(map_plot)],
        header_background='#2B3E50',
        accent_base_color='#2B3E50',
        background='#2B3E50',
    )
    template.show()
    pass


if __name__ == '__main__':
    main()
