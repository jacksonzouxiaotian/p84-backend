def generate_citation(ref, style="APA"):
    if style == "APA":
        return f"{ref.authors} ({ref.year}). {ref.title}. {ref.source}."
    elif style == "MLA":
        return f"{ref.authors}. \"{ref.title}.\" {ref.source}, {ref.year}."
    elif style == "Chicago":
        return f"{ref.authors}. {ref.title}. {ref.source}, {ref.year}."
    else:
        return f"{ref.authors} ({ref.year}). {ref.title}."