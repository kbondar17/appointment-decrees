import typer

from api.pravo_api import PravoInterface

app = typer.Typer()


@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")


@app.command()
def get_docs(gov_body: str = typer.Option(...),  date_type: str = typer.Option(...), date:str = typer.Option(''), 
            date_from=typer.Option(''), date_to=typer.Option(''), doc_number=typer.Option(''),
             key_word=typer.Option(''), filename=typer.Option('')):
    """значение gov_body должно точно соответствовать списку органов из http://pravo.gov.ru/proxy/ips/?start_search&fattrib=1 
    варианты date_type:
        1. "Точно" (тогда указывается только параметр date)
        2. "Период" (тогда указывается date_from и date_to)
        все даты в формате дд.мм.гггг

    doc_number - ведомственный номер документа
    key_word - поисковое слово (назначить, премия, здравоохранение)
    filename - куда сохранить ссылки
    """
    api = PravoInterface(gov_body=gov_body, date_type=date_type, date=date, date_from=date_from, date_to=date_to, key_word=key_word, doc_number=doc_number, filename=filename)
    api.get_docs()


if __name__ == "__main__":
    app()