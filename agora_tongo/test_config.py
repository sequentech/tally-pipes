 #-*- coding:utf-8 -*-

PIRATA_SECOND_ROUND_PIPE = (
    ('agora_tongo.pipes.stv_tiebreak.stv_first_round_tiebreak', None),
    ('agora_tongo.pipes.pretty_print.pretty_print_stv_winners', None),
)

PODEMOS_PRIMARIES_RAW_PIPE = (
    ('agora_tongo.pipes.sort_approval.sort_approval', None),
    ('agora_tongo.pipes.pretty_print.pretty_print_approval',
        dict(mark_winners=True)),
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

PODEMOS_DOCUMENTS_FINAL_PIPE = (
    (
        'agora_tongo.pipes.multipart.reduce_with_corrections',
        {
            "questions_corrections": [
    {
        "10": [
            {
                "question_id": 0,
                "answer_value": "Equipo 97",
                "tally_id": 0,
                "answer_id": 8
            },
            {
                "question_id": 0,
                "answer_value": "Equipo 97",
                "tally_id": 1,
                "answer_id": 9
            }
        ],
        "11": [
            {
                "question_id": 0,
                "answer_value": "S\u00ed se Puede",
                "tally_id": 0,
                "answer_id": 9
            },
            {
                "question_id": 0,
                "answer_value": "S\u00ed se Puede",
                "tally_id": 1,
                "answer_id": 10
            }
        ],
        "12": [
            {
                "question_id": 0,
                "answer_value": "Proceso constituyente - Equipo 159",
                "tally_id": 0,
                "answer_id": 10
            },
            {
                "question_id": 0,
                "answer_value": "Proceso constituyente - Equipo 159",
                "tally_id": 1,
                "answer_id": 11
            }
        ],
        "13": [
            {
                "question_id": 0,
                "answer_value": "La Hora de la Gente Decente",
                "tally_id": 1,
                "answer_id": 12
            }
        ],
        "8": [
            {
                "question_id": 0,
                "answer_value": "Construyendo ciudadan\u00eda para todas las personas",
                "tally_id": 0,
                "answer_id": 6
            },
            {
                "question_id": 0,
                "answer_value": "Construyendo ciudadan\u00eda para todas las personas",
                "tally_id": 1,
                "answer_id": 7
            }
        ],
        "9": [
            {
                "question_id": 0,
                "answer_value": "Equipo 64",
                "tally_id": 0,
                "answer_id": 7
            },
            {
                "question_id": 0,
                "answer_value": "Equipo 64",
                "tally_id": 1,
                "answer_id": 8
            }
        ],
        "6": [],
        "7": [
            {
                "question_id": 0,
                "answer_value": "Podemos: participaci\u00f3n, transparencia y democracia.",
                "tally_id": 0,
                "answer_id": 5
            },
            {
                "question_id": 0,
                "answer_value": "Podemos: participaci\u00f3n, transparencia y democracia.",
                "tally_id": 1,
                "answer_id": 6
            }
        ],
        "4": [
            {
                "question_id": 0,
                "answer_value": "\u00c9tica y transparencia",
                "tally_id": 0,
                "answer_id": 4
            },
            {
                "question_id": 0,
                "answer_value": "\u00c9tica y transparencia",
                "tally_id": 1,
                "answer_id": 4
            }
        ],
        "5": [
            {
                "question_id": 0,
                "answer_value": "Equipo 10 C\u00edrculos",
                "tally_id": 1,
                "answer_id": 5
            }
        ],
        "2": [
            {
                "question_id": 0,
                "answer_value": "Claro Que Podemos - Equipo Pablo Iglesias",
                "tally_id": 0,
                "answer_id": 2
            },
            {
                "question_id": 0,
                "answer_value": "Claro Que Podemos - Equipo Pablo Iglesias",
                "tally_id": 1,
                "answer_id": 2
            }
        ],
        "3": [
            {
                "question_id": 0,
                "answer_value": "Juristas Madrid",
                "tally_id": 0,
                "answer_id": 3
            },
            {
                "question_id": 0,
                "answer_value": "Juristas Madrid",
                "tally_id": 1,
                "answer_id": 3
            }
        ],
        "1": [
            {
                "question_id": 0,
                "answer_value": "Equipo Enfermeras",
                "tally_id": 0,
                "answer_id": 1
            },
            {
                "question_id": 0,
                "answer_value": "Equipo Enfermeras",
                "tally_id": 1,
                "answer_id": 1
            }
        ]
    },
    {
        "18": [
            {
                "question_id": 1,
                "answer_value": "Proceso constituyente - Equipo 159",
                "tally_id": 0,
                "answer_id": 20
            },
            {
                "question_id": 1,
                "answer_value": "Proceso constituyente - Equipo 159",
                "tally_id": 1,
                "answer_id": 19
            }
        ],
        "19": [
            {
                "question_id": 1,
                "answer_value": "Instrumento de Transformaci\u00f3n",
                "tally_id": 0,
                "answer_id": 21
            },
            {
                "question_id": 1,
                "answer_value": "Instrumento de Transformaci\u00f3n",
                "tally_id": 1,
                "answer_id": 20
            }
        ],
        "10": [
            {
                "question_id": 1,
                "answer_value": "Equipo 63",
                "tally_id": 0,
                "answer_id": 12
            },
            {
                "question_id": 1,
                "answer_value": "Equipo 63",
                "tally_id": 1,
                "answer_id": 11
            }
        ],
        "11": [
            {
                "question_id": 1,
                "answer_value": "Equipo 67",
                "tally_id": 0,
                "answer_id": 13
            },
            {
                "question_id": 1,
                "answer_value": "Equipo 67",
                "tally_id": 1,
                "answer_id": 12
            }
        ],
        "12": [
            {
                "question_id": 1,
                "answer_value": "Equipo 73",
                "tally_id": 0,
                "answer_id": 14
            },
            {
                "question_id": 1,
                "answer_value": "Equipo 73",
                "tally_id": 1,
                "answer_id": 13
            }
        ],
        "13": [
            {
                "question_id": 1,
                "answer_value": "Equipo 89",
                "tally_id": 0,
                "answer_id": 15
            },
            {
                "question_id": 1,
                "answer_value": "Equipo 89",
                "tally_id": 1,
                "answer_id": 14
            }
        ],
        "14": [
            {
                "question_id": 1,
                "answer_value": "Claro que podemos,... Democracia Ciudadana",
                "tally_id": 0,
                "answer_id": 16
            },
            {
                "question_id": 1,
                "answer_value": "Claro que podemos,... Democracia Ciudadana",
                "tally_id": 1,
                "answer_id": 15
            }
        ],
        "15": [
            {
                "question_id": 1,
                "answer_value": "Junt@s podemos",
                "tally_id": 0,
                "answer_id": 17
            },
            {
                "question_id": 1,
                "answer_value": "Junt@s podemos",
                "tally_id": 1,
                "answer_id": 16
            }
        ],
        "16": [
            {
                "question_id": 1,
                "answer_value": "Equipo 137",
                "tally_id": 0,
                "answer_id": 18
            },
            {
                "question_id": 1,
                "answer_value": "Equipo 137",
                "tally_id": 1,
                "answer_id": 17
            }
        ],
        "17": [
            {
                "question_id": 1,
                "answer_value": "Sindicalismo y modelo econ\u00f3mico",
                "tally_id": 0,
                "answer_id": 19
            },
            {
                "question_id": 1,
                "answer_value": "Sindicalismo y modelo econ\u00f3mico",
                "tally_id": 1,
                "answer_id": 18
            }
        ],
        "20": [
            {
                "question_id": 1,
                "answer_value": "Rep\u00fablica Democr\u00e1tica y Social",
                "tally_id": 0,
                "answer_id": 23
            },
            {
                "question_id": 1,
                "answer_value": "Rep\u00fablica Democr\u00e1tica y Social",
                "tally_id": 1,
                "answer_id": 21
            }
        ],
        "21": [],
        "8": [
            {
                "question_id": 1,
                "answer_value": "Con tu Voz, S\u00ed se Puede",
                "tally_id": 0,
                "answer_id": 10
            },
            {
                "question_id": 1,
                "answer_value": "Con tu Voz, S\u00ed se Puede",
                "tally_id": 1,
                "answer_id": 9
            }
        ],
        "9": [
            {
                "question_id": 1,
                "answer_value": "Equipo 60",
                "tally_id": 0,
                "answer_id": 11
            },
            {
                "question_id": 1,
                "answer_value": "Equipo 60",
                "tally_id": 1,
                "answer_id": 10
            }
        ],
        "6": [
            {
                "question_id": 1,
                "answer_value": "Construyendo Pueblo",
                "tally_id": 0,
                "answer_id": 8
            },
            {
                "question_id": 1,
                "answer_value": "Construyendo Pueblo",
                "tally_id": 1,
                "answer_id": 7
            }
        ],
        "7": [
            {
                "question_id": 1,
                "answer_value": "Con lxs trabajadorxs Podemos!",
                "tally_id": 0,
                "answer_id": 9
            },
            {
                "question_id": 1,
                "answer_value": "Con lxs trabajadorxs Podemos!",
                "tally_id": 1,
                "answer_id": 8
            }
        ],
        "4": [
            {
                "question_id": 1,
                "answer_value": "Democracia Radical",
                "tally_id": 0,
                "answer_id": 4
            },
            {
                "question_id": 1,
                "answer_value": "Democracia Radical",
                "tally_id": 1,
                "answer_id": 4
            }
        ],
        "5": [
            {
                "question_id": 1,
                "answer_value": "Democracia y Justicia Social",
                "tally_id": 0,
                "answer_id": 5
            },
            {
                "question_id": 1,
                "answer_value": "Democracia y Justicia Social",
                "tally_id": 1,
                "answer_id": 5
            }
        ],
        "2": [
            {
                "question_id": 1,
                "answer_value": "Claro Que Podemos - Equipo Pablo Iglesias",
                "tally_id": 0,
                "answer_id": 2
            },
            {
                "question_id": 1,
                "answer_value": "Claro Que Podemos - Equipo Pablo Iglesias",
                "tally_id": 1,
                "answer_id": 2
            }
        ],
        "3": [
            {
                "question_id": 1,
                "answer_value": "Juristas Madrid",
                "tally_id": 0,
                "answer_id": 3
            },
            {
                "question_id": 1,
                "answer_value": "Juristas Madrid",
                "tally_id": 1,
                "answer_id": 3
            }
        ],
        "1": [
            {
                "question_id": 1,
                "answer_value": "Equipo Enfermeras",
                "tally_id": 0,
                "answer_id": 1
            },
            {
                "question_id": 1,
                "answer_value": "Equipo Enfermeras",
                "tally_id": 1,
                "answer_id": 1
            }
        ]
    },
    {
        "21": [
            {
                "question_id": 2,
                "answer_value": "M\u00e1ximas Competencias para la Asamblea",
                "tally_id": 0,
                "answer_id": 21
            },
            {
                "question_id": 2,
                "answer_value": "M\u00e1ximas Competencias para la Asamblea",
                "tally_id": 1,
                "answer_id": 21
            }
        ],
        "20": [
            {
                "question_id": 2,
                "answer_value": "Instrumento de Transformaci\u00f3n",
                "tally_id": 0,
                "answer_id": 20
            },
            {
                "question_id": 2,
                "answer_value": "Instrumento de Transformaci\u00f3n",
                "tally_id": 1,
                "answer_id": 20
            }
        ],
        "23": [],
        "22": [
            {
                "question_id": 2,
                "answer_value": "Podemos ir M\u00e1s All\u00e1",
                "tally_id": 0,
                "answer_id": 22
            },
            {
                "question_id": 2,
                "answer_value": "Podemos ir M\u00e1s All\u00e1",
                "tally_id": 1,
                "answer_id": 22
            }
        ],
        "18": [
            {
                "question_id": 2,
                "answer_value": "Junt@s podemos",
                "tally_id": 0,
                "answer_id": 18
            },
            {
                "question_id": 2,
                "answer_value": "Junt@s podemos",
                "tally_id": 1,
                "answer_id": 18
            }
        ],
        "19": [
            {
                "question_id": 2,
                "answer_value": "Podemos M\u00e9xico. Propuesta sobre los c\u00edrculos del exterior",
                "tally_id": 0,
                "answer_id": 19
            },
            {
                "question_id": 2,
                "answer_value": "Podemos M\u00e9xico. Propuesta sobre los c\u00edrculos del exterior",
                "tally_id": 1,
                "answer_id": 19
            }
        ],
        "10": [
            {
                "question_id": 2,
                "answer_value": "Equipo 63",
                "tally_id": 0,
                "answer_id": 10
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 63",
                "tally_id": 1,
                "answer_id": 10
            }
        ],
        "11": [
            {
                "question_id": 2,
                "answer_value": "Equipo 67",
                "tally_id": 0,
                "answer_id": 11
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 67",
                "tally_id": 1,
                "answer_id": 11
            }
        ],
        "12": [
            {
                "question_id": 2,
                "answer_value": "Equipo 69",
                "tally_id": 0,
                "answer_id": 12
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 69",
                "tally_id": 1,
                "answer_id": 12
            }
        ],
        "13": [
            {
                "question_id": 2,
                "answer_value": "Entre todos s\u00ed Podemos",
                "tally_id": 0,
                "answer_id": 13
            },
            {
                "question_id": 2,
                "answer_value": "Entre todos s\u00ed Podemos",
                "tally_id": 1,
                "answer_id": 13
            }
        ],
        "14": [
            {
                "question_id": 2,
                "answer_value": "Podemos Federarnos",
                "tally_id": 0,
                "answer_id": 14
            },
            {
                "question_id": 2,
                "answer_value": "Podemos Federarnos",
                "tally_id": 1,
                "answer_id": 14
            }
        ],
        "15": [
            {
                "question_id": 2,
                "answer_value": "Equipo 89",
                "tally_id": 0,
                "answer_id": 15
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 89",
                "tally_id": 1,
                "answer_id": 15
            }
        ],
        "16": [
            {
                "question_id": 2,
                "answer_value": "Equipo 97",
                "tally_id": 0,
                "answer_id": 16
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 97",
                "tally_id": 1,
                "answer_id": 16
            }
        ],
        "17": [
            {
                "question_id": 2,
                "answer_value": "S\u00ed se Puede",
                "tally_id": 0,
                "answer_id": 17
            },
            {
                "question_id": 2,
                "answer_value": "S\u00ed se Puede",
                "tally_id": 1,
                "answer_id": 17
            }
        ],
        "8": [
            {
                "question_id": 2,
                "answer_value": "Equipo 47",
                "tally_id": 0,
                "answer_id": 8
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 47",
                "tally_id": 1,
                "answer_id": 8
            }
        ],
        "9": [
            {
                "question_id": 2,
                "answer_value": "Equipo 57",
                "tally_id": 0,
                "answer_id": 9
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 57",
                "tally_id": 1,
                "answer_id": 9
            }
        ],
        "6": [
            {
                "question_id": 2,
                "answer_value": "Equipo 9",
                "tally_id": 0,
                "answer_id": 6
            },
            {
                "question_id": 2,
                "answer_value": "Equipo 9",
                "tally_id": 1,
                "answer_id": 6
            }
        ],
        "7": [
            {
                "question_id": 2,
                "answer_value": "Sumamos",
                "tally_id": 0,
                "answer_id": 7
            },
            {
                "question_id": 2,
                "answer_value": "Sumamos",
                "tally_id": 1,
                "answer_id": 7
            }
        ],
        "4": [
            {
                "question_id": 2,
                "answer_value": "Sumando Podemos",
                "tally_id": 0,
                "answer_id": 4
            },
            {
                "question_id": 2,
                "answer_value": "Sumando Podemos",
                "tally_id": 1,
                "answer_id": 4
            }
        ],
        "5": [
            {
                "question_id": 2,
                "answer_value": "Decide la Ciudadan\u00eda",
                "tally_id": 0,
                "answer_id": 5
            },
            {
                "question_id": 2,
                "answer_value": "Decide la Ciudadan\u00eda",
                "tally_id": 1,
                "answer_id": 5
            }
        ],
        "2": [
            {
                "question_id": 2,
                "answer_value": "Claro Que Podemos - Equipo Pablo Iglesias",
                "tally_id": 0,
                "answer_id": 2
            },
            {
                "question_id": 2,
                "answer_value": "Claro Que Podemos - Equipo Pablo Iglesias",
                "tally_id": 1,
                "answer_id": 2
            }
        ],
        "3": [
            {
                "question_id": 2,
                "answer_value": "Juristas Madrid",
                "tally_id": 0,
                "answer_id": 3
            },
            {
                "question_id": 2,
                "answer_value": "Juristas Madrid",
                "tally_id": 1,
                "answer_id": 3
            }
        ],
        "1": [
            {
                "question_id": 2,
                "answer_value": "Equipo Enfermeras",
                "tally_id": 0,
                "answer_id": 1
            },
            {
                "question_id": 2,
                "answer_value": "Equipo Enfermeras",
                "tally_id": 1,
                "answer_id": 1
            }
        ]
    }
]

        }
    ),
    ('agora_tongo.pipes.sort_approval.sort_approval', None),
    ('agora_tongo.pipes.pretty_print.pretty_print_approval',
        dict(mark_winners=True)),
)