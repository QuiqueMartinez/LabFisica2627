# Cuadernillos

Un cuadernillo puede ser **cualquier cosa**. No tiene por qué seguir el estilo
de las sesiones: ni dos columnas, ni Montserrat, ni los márgenes del dossier.

Lo único que se le pide es un `meta.tex` en su carpeta. Ese fichero es lo que
el generador web lee para ponerlo en el índice, y es lo que permite listar algo
sin tener que compilarlo ni entender cómo está hecho.

## Las tres formas

```
quaderns/
├── vectors/                  1. maqueta propia, fuente LaTeX
│   ├── meta.tex
│   ├── vectors.tex           (su propio \documentclass y su preámbulo)
│   └── images/
├── quimica_t1/               2. maquetado a mano, sin fuente
│   ├── meta.tex              (con  pdf = {quimica_t1.pdf})
│   └── quimica_t1.pdf        (Affinity)
└── unitats/                  3. reutiliza el estilo de las sesiones
    ├── meta.tex
    ├── continguts.tex
    └── images/
```

**1. Maqueta propia.** Lo normal si el cuadernillo pide otra composición. Lleva
su propio `\documentclass` y su preámbulo, y se compila solo. No pasa por
`\sessio` ni por `\lfUnitat`, que heredan el preámbulo del dossier.

**2. Sin fuente.** El `meta.tex` lleva el campo `pdf`. No hay nada que
compilar: ese PDF es el original, es irrecuperable, y por eso **sí se
commitea**. El `.gitignore` tiene una excepción para los PDF de esta carpeta.

La contrapartida de esa excepción: no compiles aquí dentro. La salida de
`latexmk` junto a un `.tex` de esta carpeta acabaría versionada por error. Los
PDF generados van a `/build/`.

**3. Reutilizando el estilo de las sesiones.** Solo si lo quieres a propósito.
Entonces vale `\lfUnitat{quaderns/unitats}{continguts}`, que no aporta estilo:
resuelve las imágenes y escribe la cabecera leyendo el `meta.tex`.

## La cabecera

Si `numero` está vacío, la cabecera es solo el `titol`, sin «Sessió N». Un
cuadernillo no es una sessió.
