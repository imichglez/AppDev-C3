# Conjunto Mínimo de Lexemas para Clasificación de Paradigmas de Código

Este es un conjunto mínimo de lexemas (palabras clave y tokens significativos como `class`, `function`, `{ }`, `;`, etc.). El objetivo de este conjunto es permitir la clasificación de un archivo de texto como **Programación Orientada a Objetos (POO)**, **Programación Procedimental**, **Híbrido** (mezcla de ambos), o **Texto plano/Sin código**. Esta clasificación se basa únicamente en la presencia y frecuencia de estos lexemas, utilizando características léxicas sin realizar un análisis sintáctico completo o semántico del código.

---

## 1. `class`

* **Justificación:** La palabra clave fundamental absoluta para definir clases en la mayoría de los lenguajes POO principales (Java, C++, C#, Python, etc.). Su presencia es un indicador muy fuerte de Programación Orientada a Objetos.
* **Ejemplo:** `class MyClass { ... }` (Java/C#), `class MyClass: ...` (Python)
* **Influencia:** Una alta frecuencia sugiere fuertemente POO o Híbrido. La ausencia hace improbable la clasificación como POO pura (aunque no imposible si se usan palabras clave alternativas como `prototype` en JavaScript, lo que complica este modelo mínimo).

## 2. `struct`

* **Justificación:** Representa tipos de datos compuestos definidos por el usuario. Fuertemente asociado con lenguajes Procedimentales (como C) para agrupar datos. También presente en algunos lenguajes POO (como C++) donde puede comportarse de manera similar a una clase (pero los miembros son públicos por defecto). Su presencia puede indicar gestión de datos de estilo procedimental o estructuras de datos más simples en contextos POO/Híbridos.
* **Ejemplo:** `struct Point { int x; int y; };` (C/C++)
* **Influencia:** La presencia junto a `function` pero sin palabras clave fuertes de POO (como `class`, `private`) podría inclinarse hacia Procedimental. La presencia en código C++ podría ser Híbrido o POO. Su distinción de `class` puede depender del lenguaje.

## 3. `function` / `def` / `sub` (Tratar como equivalentes)

* **Justificación:** Palabras clave usadas para definir procedimientos, funciones o subrutinas, que son los bloques de construcción de la programación Procedimental. También se usan para definir métodos dentro de clases en POO. Esenciales para identificar construcciones procedimentales *y* métodos en POO. Incluye variantes comunes (`def` para Python, `sub` para lenguajes tipo VB).
* **Ejemplo:** `function calculate(x) { ... }` (JavaScript), `def calculate(x): ...` (Python), `Sub Calculate(x) ... End Sub` (VB)
* **Influencia:** Se espera una alta frecuencia tanto en código Procedimental como POO/Híbrido. Si se encuentra *sin* palabras clave significativas de POO (`class`, `new`, modificadores de acceso), sugiere fuertemente Procedimental. Si se encuentra dentro de bloques `class` o junto a palabras clave de POO, contribuye a la clasificación POO/Híbrida.

## 4. `public` / `private` / `protected` (Tratar como indicadores de control de acceso)

* **Justificación:** Los modificadores de acceso son fundamentales para el concepto de encapsulamiento de la POO, controlando la visibilidad de los miembros de la clase. Su presencia indica fuertemente una intención de estructurar el código de manera orientada a objetos.
* **Ejemplo:** `private int count;` (Java/C#), `public function getName() { ... }` (PHP/Java)
* **Influencia:** La presencia sugiere fuertemente POO o Híbrido. La ausencia no descarta la POO (p. ej., Python usa convenciones como guiones bajos iniciales), pero la presencia es una señal positiva fuerte.

## 5. `new`

* **Justificación:** Palabra clave usada en muchos lenguajes POO importantes (Java, C#, C++, JavaScript) para instanciar explícitamente un objeto (crear una instancia de una clase). Se relaciona directamente con el aspecto de creación de objetos de la POO.
* **Ejemplo:** `MyClass obj = new MyClass();` (Java/C#)
* **Influencia:** La presencia es un fuerte indicador de POO o Híbrido, apuntando específicamente hacia la creación dinámica de objetos.

## 6. `this` / `self` (Tratar como referencias de instancia equivalentes)

* **Justificación:** Palabras clave usadas dentro de los métodos de clase para referirse a la instancia actual del objeto. Esenciales para operaciones específicas del objeto y gestión del estado en POO. `this` es común en Java, C++, C#, JavaScript; `self` es estándar en Python.
* **Ejemplo:** `this.member = value;` (Java/C++), `self.member = value` (Python)
* **Influencia:** La presencia sugiere fuertemente POO o Híbrido, ya que están intrínsecamente ligados al concepto de operar sobre los propios datos o métodos de un objeto.

## 7. `.` (Operador Punto)

* **Justificación:** Usado ubicuamente en muchos lenguajes para acceder a miembros (propiedades o métodos) de un objeto (POO) o campos de una estructura (Procedimental/POO). Aunque no es exclusivo de un paradigma, su patrón de uso a menudo difiere.
* **Ejemplo:** `objeto.metodo()`, `instancia_struct.campo`
* **Influencia:** Una alta frecuencia, especialmente combinada con identificadores que probablemente representan objetos (a menudo siguiendo a `new` o siendo parámetros llamados `self`/`this`), refuerza la clasificación POO/Híbrida. Su presencia junto a variables `struct` sugiere estructuras de datos Procedimentales o básicas. Su mera frecuencia ayuda a distinguir el código del texto plano.

## 8. `extends` / `implements` / `:` (en contexto de definición de clase - Tratar como indicadores de herencia/interfaz)

* **Justificación:** Palabras clave o sintaxis que definen la herencia (heredar características de una clase padre) o la implementación de interfaces, que son conceptos centrales en POO que promueven la reutilización de código y el polimorfismo. Los dos puntos (`:`) se usan para la herencia en C++ y C#.
* **Ejemplo:** `class Dog extends Animal { ... }` (Java), `class MyClass : IMyInterface { ... }` (C#), `class Derived : public Base { ... }` (C++)
* **Influencia:** La presencia es un indicador muy fuerte de patrones de diseño POO o Híbridos.

## 9. `{` y `}` (Llaves)

* **Justificación:** Usadas en muchos lenguajes estilo C (C, C++, Java, C#, JavaScript) para delimitar bloques de código (funciones, clases, estructuras de control). Su presencia equilibrada es un fuerte indicador de código estructurado, común tanto en Procedimental como en POO en estos lenguajes.
* **Ejemplo:** `if (x > 0) { ... }`, `class MyClass { ... }`
* **Influencia:** Una alta frecuencia sugiere código estructurado (Procedimental, POO, Híbrido). La ausencia (o reemplazo por indentación como en Python) no descarta el código pero apunta hacia diferentes familias sintácticas. Crucial para diferenciar el código del texto plano no estructurado.

## 10. `;` (Punto y coma)

* **Justificación:** Usado como terminador de sentencia en muchos lenguajes Procedimentales y POO influyentes (C, C++, Java, C#).
* **Ejemplo:** `int a = 5;`, `objeto.hacerAlgo();`
* **Influencia:** Una alta frecuencia sugiere fuertemente código de la familia estilo C (Procedimental, POO, Híbrido). Su ausencia es típica de lenguajes como Python o texto plano. Ayuda a distinguir estilos de código e identificar texto no código.

---

## Esquema Lógico de Clasificación:

* **POO:** Alta frecuencia de `class`, modificadores de acceso (`public`/`private`), `new`, `this`/`self`, palabras clave de herencia (`extends`/`implements`/`:`) a menudo combinadas con `.`, `function`/`def`.
* **Procedimental:** Alta frecuencia de `function`/`def`, posiblemente `struct`, estructuras de código comunes (`{ }`, `;`, `.`) pero frecuencia *baja o nula* de palabras clave centrales de POO (`class`, `new`, modificadores de acceso, `this`/`self`, palabras clave de herencia).
* **Híbrido:** Presencia significativa de *ambas* palabras clave centrales de POO (`class`, `new`, etc.) *y* potencialmente `function`/`def` independientes o uso intensivo de `struct` junto a clases. Muchos lenguajes modernos caerían aquí.
* **Texto plano / Sin código:** Frecuencia muy baja o ausencia completa de la mayoría de las palabras clave y tokens estructurales anteriores (`{ }`, `;`, `.`). Mayor proporción de palabras del lenguaje natural y puntuación no utilizada en un contexto de sintaxis de código.
