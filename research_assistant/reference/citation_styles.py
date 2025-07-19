def generate_citation(ref, style="APA"):
    if style.upper() == "APA":
        return f"{ref.authors} ({ref.year}). {ref.title}. {ref.source}."
    elif style.upper() == "MLA":
        return f"{ref.authors}. \"{ref.title}.\" {ref.source}, {ref.year}."
    elif style.upper() == "CHICAGO":
        return f"{ref.authors}. \"{ref.title}.\" {ref.source} ({ref.year})."
    else:
        return "Unsupported style"