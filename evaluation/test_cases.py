TEST_CASES = [
    {
        "name": "gestión general de vacaciones",
        "query": (
            "¿Cómo se gestionan las vacaciones?"
        ),
        "expected_has_context": True,
        "expected_pages": [5, 6, 7, 19],
    },
    {
        "name": "solicitud de vacaciones",
        "query": (
            "¿Cómo se deben solicitar las vacaciones?"
        ),
        "expected_has_context": True,
        "expected_pages": [6],
    },
    {
        "name": "aprobación de vacaciones",
        "query": (
            "¿Cuándo se consideran aprobadas las vacaciones?"
        ),
        "expected_has_context": True,
        "expected_pages": [6],
    },
    {
        "name": "vacaciones e incapacidad temporal",
        "query": (
            "¿Qué ocurre si una persona está de baja "
            "durante sus vacaciones?"
        ),
        "expected_has_context": True,
        "expected_pages": [7, 9],
    },
    {
        "name": "duración de la jornada laboral",
        "query": (
            "¿Cómo se determina la duración "
            "de la jornada laboral?"
        ),
        "expected_has_context": True,
        "expected_pages": [2, 3, 4],
    },
    {
        "name": "tipos de jornada laboral",
        "query": (
            "¿Qué tipos de jornada laboral existen?"
        ),
        "expected_has_context": True,
        "expected_pages": [2],
    },
    {
        "name": "tipos de permisos",
        "query": (
            "¿Qué tipos de permisos pueden solicitar "
            "las personas trabajadoras?"
        ),
        "expected_has_context": True,
        "expected_pages": [8],
    },
    {
        "name": "solicitud de permisos",
        "query": (
            "¿Qué debe hacer una persona trabajadora "
            "para solicitar un permiso?"
        ),
        "expected_has_context": True,
        "expected_pages": [8],
    },
    {
        "name": "pregunta fuera del dominio - cocina",
        "query": (
            "¿Cuál es la receta para hacer una tortilla "
            "de patatas?"
        ),
        "expected_has_context": False,
        "expected_pages": [],
    },
    {
        "name": "pregunta fuera del dominio - tecnología",
        "query": (
            "¿Cómo se instala PostgreSQL en un servidor?"
        ),
        "expected_has_context": False,
        "expected_pages": [],
    },
]