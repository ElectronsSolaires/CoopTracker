from datetime import timedelta
import plotly

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def fix_locale_htmlfile(filename):
    f = open(filename,'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace("<head>","<head><script src='https://cdn.plot.ly/plotly-locale-fr-latest.js'></script>")
    f = open(filename,'w')
    f.write(newdata)
    f.close()

def save_fig(fig, filename,file_path):
    fig.write_image(file_path + filename + ".png",scale=2.5, width=900)
    plotly.offline.plot(fig, filename = file_path + filename + ".html", auto_open=False, include_plotlyjs='cdn', config=dict(locale='fr', displayModeBar=False))
    fix_locale_htmlfile(file_path + filename + ".html")
    #fig.show(config=dict(locale='fr', displayModeBar=False))