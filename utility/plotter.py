import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker
from matplotlib.cm import get_cmap


def plot_articles(all_articles, search_terms):
    (df, grouped, total_articles_per_outlet, grouped_terms, extrapolated_last_two_terms,
     total_articles_per_search_term) = (prepare_data(all_articles, search_terms))

    # Plot the data
    plot_data(df, grouped, total_articles_per_outlet, grouped_terms,extrapolated_last_two_terms,
              total_articles_per_search_term, search_terms)


def prepare_data(articles, search_terms):
    data = []
    for a in articles:
        for term in a.search_terms:
            if term in search_terms:
                data.append({
                    'outlet': a.news_outlet.name,
                    'color': a.news_outlet.color,
                    'date': a.date,
                    'search_term': term
                })

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    grouped = df.groupby('outlet').resample('QE').size().unstack(fill_value=0)
    total_articles_per_outlet = grouped.sum(axis=1)

    grouped_terms = df.groupby('search_term').resample('YE').size().unstack(fill_value=0)

    grouped_terms_last_two_periods = grouped_terms.iloc[:, [-2, -1]]
    extrapolated_last_two_terms = extrapolate_data(grouped_terms_last_two_periods)

    total_articles_per_search_term = grouped_terms.sum(axis=1)

    grouped['Total'] = total_articles_per_outlet
    grouped.sort_values('Total', ascending=False, inplace=True)
    del grouped['Total']

    return (df, grouped, total_articles_per_outlet, grouped_terms,extrapolated_last_two_terms,
            total_articles_per_search_term)


def plot_data(df, grouped, total_articles_per_outlet, grouped_terms, extrapolated_last_two_terms,
              total_articles_per_search_term, search_terms):
    # Create a plot
    fig, ax = plt.subplots(figsize=(18, 9))

    # Title setup
    if len(search_terms) > 1:
        quoted_strings = ['"' + s + '"' for s in search_terms]
        ax.set_title(f'Frequency of Search Terms {", ".join(quoted_strings)} in German News Coverage')
    elif len(search_terms) == 1:
        ax.set_title(f'Frequency of Search Term "{search_terms[0]}" in German News Coverage')
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Number of Articles per annual Quarter')

    def minor_tick_formatter(x, pos):
        date = mdates.num2date(x)
        if date.month in [1, 4, 7, 10]:
            return f"{(date.month // 3) % 4 + 1}"  # Return the quarter number
        return ''

    # Formatting x-axis
    # Set x-axis major and minor ticks
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_formatter(ticker.FuncFormatter(minor_tick_formatter))

    # Customize tick label appearance
    ax.tick_params(axis='x', which='major', pad=15, rotation=45, top=False)  # Adjust padding for major ticks
    ax.tick_params(axis='x', which='minor', colors='grey')  # Color for minor ticks

    ax2 = ax.twinx()  # Create a twin axis

    # Color map for search terms
    cmap = get_cmap('Pastel1')
    colors = [cmap(i) for i in range(len(search_terms))]

    # Plotting for each news outlet
    bottom = None
    for outlet in grouped.index:
        color = df[df['outlet'] == outlet]['color'].iloc[0]
        # Shift the position of bars to represent the beginnings of quarters
        bar_positions = [datetime(date.year, ((date.month - 1) // 3) * 3 + 1, 1) for date in grouped.columns]
        ax.bar(bar_positions, grouped.loc[outlet], bottom=bottom, color=color, width=50,
               label=f"{outlet}: {total_articles_per_outlet[outlet]}")
        if bottom is None:
            bottom = grouped.loc[outlet]
        else:
            bottom += grouped.loc[outlet]

    # Plotting for each search term
    for i, term in enumerate(search_terms):
        if term in grouped_terms.index:
            # Convert datetime index to PeriodIndex with frequency 'A' (annual) and subtract one to shift the lines
            idx = pd.PeriodIndex(grouped_terms.columns.to_period('Y'))
            ax2.plot(idx.to_timestamp(), grouped_terms.loc[term], marker='o', linestyle='-', markersize=3,
                     label=f"{term}: {total_articles_per_search_term[term]}", color=colors[i])
        if term in extrapolated_last_two_terms.index:
            idx = pd.PeriodIndex(extrapolated_last_two_terms.columns.to_period('Y'))
            ax2.plot(idx.to_timestamp(), extrapolated_last_two_terms.loc[term], marker='^', linestyle='dotted',
                     markersize=3, color=colors[i])

    # Single legend for all items
    handles, labels = [], []
    for ax in [ax, ax2]:
        for handle, label in zip(*ax.get_legend_handles_labels()):
            handles.append(handle)
            labels.append(label)
    ax.legend(handles, labels, title='# of Results by News Outlet and Search Term')

    ax2.set_ylabel('Annual Frequencies of Search Terms ')

    plt.tight_layout()
    plt.show()


def extrapolate_data(df):
    # Current date
    today = datetime.now()
    # Calculate the fraction of the year that has passed
    start_of_year = datetime(today.year, 1, 1)
    end_of_year = datetime(today.year, 12, 31)
    days_in_year = (end_of_year - start_of_year).days + 1
    days_passed = (today - start_of_year).days + 1
    fraction_of_year_passed = days_passed / days_in_year

    # Access the last column of the DataFrame
    last_column = df.iloc[:, -1]

    # Extrapolate data based on the fraction of the year passed and round to nearest integer
    df.iloc[:, -1] = (last_column / fraction_of_year_passed).round(0).astype(int)

    # Return the modified DataFrame
    return df
