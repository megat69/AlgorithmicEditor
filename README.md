# AlgorithmicEditor
An internal and personal tool to parse pseudocode into algorithmic french.

Please don't look at the code. For real. It was thrown together in a couple of days, and maintained since.

## Syntax
### Variables declaration / Déclaration de Variables
***ENGLISH***<br>
A variable is declared using the following syntax : `<type> <name>`

The available types are the following :
- `int`
- `float`
- `bool`
- `char`
- `string`

You can also declare multiple variables at once by putting a space between them as so :<br>
`<type> <var1> [var2] [var3] [...]`


***FRANÇAIS***<br>
Une variable est déclarée grâce à la syntaxe suivante : `<type> <nom>`

Les types existants sont les suivants :
- `int` (nombre entier)
- `float` (réel)
- `bool` (booléen)
- `char` (caractère)
- `string` (chaîne de caractères)

Vous pouvez aussi déclarer plusieurs variables en une fois en les séparant par un espace comme suit :<br>
`<type> <var1> [var2] [var3] [...]`

**EXAMPLE/EXEMPLE**<br>
```
string name
int age i
```

### Variables assignation / Assignement de Valeurs
***ENGLISH***<br>
You can assign a value to variables just like you would in any programming language, as long as the variable has been declared beforehand : `<name> = <expression>`

The editor supports any type of operator (`=`, `+=`, `-=`, `*=`, ...).

***FRANÇAIS***<br>
Vous pouvez assigner une valeur à une variable de la même manière que dans n'importe quel langage de programmation, tant que la variable a été déclarée précédemment : `<nom> = <expression>`

L'éditeur supporte n'importe quel opérateur (`=`, `+=`, `-=`, `*=`, ...).


### Loops
***ENGLISH***<br>
Two types of loops exist within the editor : the `for` and the `while` loops.

#### `for` loops<br>
The for loop will increment from a start number to and end number with the given step (1 by default). It will store this value in a given variable, **which must be declared beforehand.**

Syntax :<br>
```
for <var> <min> <max> [step=1]
<instructions>
end
```

Examples :<br>
```
for i 0 10
print i & "(ENDL)"
end

for i 0 10 2
print i & " is even."
end
```

#### `while` loops<br>
This loop will loop while the condition given to it is true.

Syntax :<br>
```
while <condition>
<instructions>
end
```

Example :<br>
```
int nbr
nbr = 0
while nbr < 10 OU nbr > 30
print "Input an number between 10 and 30"
input nbr
end
```

***FRANÇAIS***<br>
Deux types de boucles existent dans l'éditeur : la boucle `for` et la boucle `while`.

#### La boucle `for`<br>
La boucle `for` va incrémenter depuis un nombre de départ jusqu'à un nombre de fin avec le pas donné (1 par défaut). Elle va stocker cette valeur dans la variable donnée, **qui doit être déclarée auparavant.**

Syntaxe :<br>
```
for <var> <min> <max> [pas=1]
<instructions>
end
```

Exemples :<br>
```
for i 0 10
print i & "(ENDL)"
end

for i 0 10 2
print i & " est pair."
end
```

#### La boucle `while`<br>
Cette boucle va boucler tant que sa condition est vraie.

Syntaxe :<br>
```
while <condition>
<instructions>
end
```

Exemple :<br>
```
int nbr
nbr = 0
while nbr < 10 OU nbr > 30
print "Entrez un nombre compris entre 10 et 30"
input nbr
end
```

### Conditions / Structures Conditionnelles
***ENGLISH***<br>
This statement will execute only if the given condition is true. Otherwise, it will move through each `elif` block, one at a time, to execute those if their condition is true, otherwise move to the `else` statement.

`elif` statements can stack. `elif` and `else` statements are optional.

You can use the keywords `ET` (AND), `OU` (OR), and `NON` (NOT), to combine conditions.

Syntax :<br>
```
if <condition>
<instructions>
elif <condition>
<instructions>
else
<instructions>
end
```

Example :<br>
```
if i % 2 == 0
print i & " is even !"
else
print i & " is odd."
```

***FRANÇAIS***<br>
Cette instruction va s'exécuter uniquement si la condition donnée vaut vrai. Sinon, elle parcourera chaque `elif`, un par un, et éxécuter ceux-ci si leur condition vaut vrai, sinon exécutera le contenu du bloc `else`.

Vous pouvez utiliser les mots-clés `ET`, `OU`, et `NON`, pour combiner des conditions.

Les instructions `elif` peuvent s'empiler. Les instructions `elif` et `else` sont facultatives.

Syntaxe :<br>
```
if <condition>
<instructions>
elif <condition>
<instructions>
else
<instructions>
end
```

Exemple :<br>
```
if i % 2 == 0
print i & " est pair !"
else
print i & " est impair."
```

### I/O operations / Opérations d'Entrée/Sortie
***ENGLISH***<br>
Two statements allow to communicate with the user : `print` and `input`.

The `print` statement allows to output text to the screen.<br>
Any text must be between quotes and will be highlighted yellow in the editor.<br>
You can combine strings and inject variables in between by closing the text with a quote and adding ` & ` (spaces matter).<br>
You can return to the line with the `(ENDL)` keyword. This keyword **MUST** be within a string.

Example :<br>
```
print "Hello, " & name & " !(ENDL)"
```

The `input` statement allows the user to input text into a variable.

Example :<br>
```
string name
input name

int age
print "Input your age"
input age
```

***FRANÇAIS***<br>
Deux instructions peuvent être utilisées pour communiquer avec l'utilisateur : `print` et `input`.

L'instruction `print` permet d'afficher du texte à l'écran.<br>
Tout texte doit être entre guillemets et sera coloré en jaune dans l'éditeur.<br>
Vous pouvez combiner des chaînes de caractères et injecter des variables entre elles en fermant le texte avec un guillement et en ajoutant ` & ` (*les espaces comptent*).<br>
Vous pouvez retourner à la ligne avec le mot-clé `(ENDL)`. Ce mot-clé **DOIT** être dans une chaîne de caractères.

Exemple :<br>
```
print "Bonjour, " & prenom & " !(ENDL)"
```

L'instruction `input` permet à l'utilisateur de rentrer du texte dans une variable.

Exemple :<br>
```
string prenom
input prenom

int age
print "Entrez votre age"
input age
```