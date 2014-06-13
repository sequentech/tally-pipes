 #-*- coding:utf-8 -*-

PIRATA_SECOND_ROUND_PIPE = (
    ('agora_tongo.pipes.stv_tiebreak.stv_first_round_tiebreak', None),
    ('agora_tongo.pipes.pretty_print.pretty_print_stv_winners', None),
)

PODEMOS_PRIMARIES_RAW_PIPE = (
    ('agora_tongo.pipes.sort_approval.sort_approval', None),
    ('agora_tongo.pipes.pretty_print.pretty_print_approval',
        dict(mark_winners=False)),
)

PODEMOS_PRIMARIES_FINAL_PIPE = (
    ('agora_tongo.pipes.sort_approval.sort_approval', dict(
        show_ties=True,
        withdrawals=['Antonio Manuel Rodríguez'])),
    ('agora_tongo.pipes.podemos_tiebreak.podemos_tiebreak', None),
    ('agora_tongo.pipes.parity.parity_zip_approval', dict(women_names=[
        'Estefanía Schweich Temprano',
        'Marta Beatriz Pérez Cabanillas',
        'Paula Quinteiro Araujo',
        'María de los Ángeles Valero Ruiz',
        'Lola Sánchez',
        'Olga Arnaiz Zhuravleva',
        'Emma Córdoba Sánchez',
        'Virginia Elena Hernandez Bauve',
        'Sandra Mínguez Corral',
        'Gloria Pilar Santiago Camacho',
        'Ana Gloria Sánchez Ruano',
        'Mª Teotiste Pérez Sanz',
        'María Isabel Pereira Varela',
        'Silvia Pineda',
        'Teresa Rodríguez Rubio',
        'Amelia Martínez Lobo',
        'Jessica del Saz Camacho',
        'Isabel Meroño Pajares',
        'Mª Isabel Espes Repolles',
        'Esperanza Jubera García',
        'Rosa Maria Bargalló Gasol',
        'Beatriz de Lara García',
        'María del Mar Millán García',
        'Maitane Huarte Vicente',
        'Lucía Montejo Arnáiz',
        'Mónica Mota Gómez',
        'Vanessa Millán',
        'Tania González',
        'Patricia Amaya Silva',
        'Beatriz Rilova Barriuso',
        'Ines Rodriguez Cachera',
        'Lucia Ayala Asensio',
        'Carmen Yuste Aguilar',
        'Amaia Borda García',
        'María José Bonilla León',
        'Ana Villaverde',
        'Mercedes Real Zarco',
        'Mª Eugenia García Nemocon',
        'Benita Fernandez Árias',
        'Carmen Caramés Díaz',
        'Nazaret Troya Cala',
        'Cristina Andrés Moya',
        'Itxaso Cabrera Gil',
        'Gema González de Chávez Menéndez',
        'Virginia Muñoz Mardones',
        'Estefanía Torres Martínez',
        'Susana Figueroa Conde-Valvíz',
        'Pilar de la Paz Martinez',
        'Cecilia Salazar-Alonso Revuelta',
        'Juana María Ripoll Alberti',
        'María Eugenia López',
        'Paloma Aldir',
        'Isabel Serra Sánchez'
    ])),
    ('agora_tongo.pipes.agora_result.result_to_file',
        dict(path="podemos_results.json")),
    ('agora_tongo.pipes.pretty_print.pretty_print_approval', None),
)


MULTIREFERENDUM_RAW_PIPE = (
    ('agora_tongo.pipes.pretty_print.pretty_print_one_choice',
        dict(mark_winners=True)),
)

PODEMOS_CONFTEAM_RAW_PIPE = (
    ('agora_tongo.pipes.pretty_print.pretty_print_approval',
        dict(mark_winners=True)),
)