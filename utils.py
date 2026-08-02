from datetime import timedelta
import plotly
import plotly.io as pio


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def fix_locale_htmlfile(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        filedata = f.read()
    newdata = filedata.replace("<head>", "<head><script src='https://cdn.plot.ly/plotly-locale-fr-latest.js'></script>")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(newdata)


def save_fig(fig, filename, file_path):
    fig.update_layout(paper_bgcolor="rgb(0,0,0,0)")
    html = pio.to_html(
        fig,
        full_html=True,
        include_plotlyjs='cdn',
        config=dict(locale='fr', displayModeBar=False),
    )
    with open(file_path + filename + ".html", 'w', encoding='utf-8') as f:
        f.write(html)
    fix_locale_htmlfile(file_path + filename + ".html")
    #fig.show(config=dict(locale='fr', displayModeBar=False))
