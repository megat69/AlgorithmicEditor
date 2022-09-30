# AlgorithmicEditor
An internal and personal tool to parse pseudocode into algorithmic french.

![image](https://img.shields.io/github/languages/code-size/megat69/AlgorithmicEditor)
![image](https://img.shields.io/tokei/lines/github/megat69/AlgorithmicEditor)
![image](https://img.shields.io/badge/Version%20support-3.7%2B-green)
![image](https://img.shields.io/github/commit-activity/m/megat69/AlgorithmicEditor)

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


### Switch / Selon
***ENGLISH***<br>
The `switch` statement allows to have a simpler algorithm than a bunch of if/elif/else statements.<br>
It takes as argument one character or integer, and then triggers the corresponding `case` block. If there is no corresponding `case` block, it defaults to the optional `default` block. You can have as many `case` blocks as you want.

Syntax :<br>
```
switch <char|int>
case <char|int>
<instructions>
end
case <char|int>
<instructions>
end
default
<instructions>
end
end
```

Example :<br>
```
int color_nbr
input color_nbr
string color

switch color_nbr
case 0
color = "black"
end
case 1
color = "red"
end
case 2
color = "green"
end
case 3
color = "blue"
end
default
color = "white"
end

print color
```

***FRANÇAIS***<br>
L'instruction `switch` permet d'avoir un algorithme plus simple qu'un tas de if/elif/else imbriqués.<br>
Elle prend comme argument un caractère ou un entier, et déclenche le bloc `case` correspondant. Si aucun bloc `case` ne correspond, elle se tourne vers le bloc optionnel par défaut `default`. Vous pouvez avoir autant de blocs `case` que vous voulez.

Syntaxe :<br>
```
switch <char|int>
case <char|int>
<instructions>
end
case <char|int>
<instructions>
end
default
<instructions>
end
end
```

Exemple :<br>
```
int nombre_couleur
input nombre_couleur
string couleur

switch nombre_couleur
case 0
couleur = "black"
end
case 1
couleur = "red"
end
case 2
couleur = "green"
end
case 3
couleur = "blue"
end
default
couleur = "white"
end

print color
```

### Functions & Procedures / Fonctions et Procédures
***ENGLISH***
Functions are pieces of code returning a specific value that are reusable anywhere in your code.<br>
Procedures are special functions which simply do an action, but return nothing.<br>
Functions and Procedures can have any number of arguments passed to them.

A function starts with the keyword `fx`, and its body begins after the `fx_start` keyword.<br>
In-between those two are some comments indicating the function's inner workings for any developper who might try to understand it.
A function uses the `return` keyword to return a value.

Syntax :<br>
```
fx <return_type> <name> [arg1_type] [arg1_name] [arg2_type] [arg2_name] [...]
[precond <text> -> What is necessary for the function to work]
[data <text> -> Which arguments are required for the function and why]
[result <text> -> What the function returns]
[desc <text> -> How the function works]
[vars -> below this instruction is the declaration of all the local variables used in the function]
fx_start
<instructions>
return <value|expression|variable> -> Can be placed anywhere within the instructions
end
```
A procedure works the exact same way, except it doesn't define a `result` comment, has `void` as a return_type (indicated in red instead of yellow in the editor) and doesn't use the `return` keyword.
```
fx void <name> [arg1_type] [arg1_name] [arg2_type] [arg2_name] [...]
[precond <text> -> What is necessary for the function to work]
[data <text> -> Which arguments are required for the function and why]
[desc <text> -> How the function works]
[vars -> below this instruction is the declaration of all the local variables used in the function]
fx_start
<instructions>
end
```

Examples :
```
fx bool isMultiple int n int x
data Two integers (n and x)
results Returns whether x is a divider of n
fx_start
return n % x == 0
end

fx void drawLine int n char c
data A integer (n) indicating the length of the line ; a character (c) indicating which character is used to fill the line.
desc Draws a line of c with length n
vars
int i
fx_start
for i 0 n
print c
end
print "(ENDL)"
end
```

***FRANÇAIS***
Les fonctions sont des bouts de code retournant une valeur spécifique qui sont réutilisables partout dans le code.<br>
Les procédures sont des fonctions particulières qui effectuent simplement une action, mais ne retourne rien.<br>
Les fonctions et procédures peuvent avoir autant de paramètres que voulu.

Une fonction commence avec le mot-clé `fx`, et son corps commence après le mot-clé `fx_start`.<br>
Entre ces deux sont des commentaires qui indiquent le fonctionnement de la fonction pour tout développeur qui voudrait essayer de la comprendre.
Une fonction utilise le mot-clé `return` pour retourner une valeur.

Syntaxe :<br>
```
fx <type_de_retour> <nom> [arg1_type] [arg1_nom] [arg2_type] [arg2_nom] [...]
[precond <text> -> Les conditions nécessaires au fonctionnement de la fonction]
[data <text> -> Quels paramètres sont nécessaires à la fonction et pourquoi]
[result <text> -> Ce que la fonction retourne]
[desc <text> -> Comment la fonction fonctionne]
[vars -> En-dessous de ceci se trouve toutes les déclarations de variables locales utilisées par la fonction]
fx_start
<instructions>
return <valeur|expression|variable> -> Peut être placé n'importe où parmi les instructions
end
```
Une procédure fonctionne de la même manière, mais elle n'utilise pas de commentaire `result`, a un type de retour de `void` (indiqué en rouge au lieu de jaune dans l'éditeur) et n'utuilise pas le mot-clé `return`.
```
fx void <nom> [arg1_type] [arg1_nom] [arg2_type] [arg2_nom] [...]
[precond <text> -> Les conditions nécessaires au fonctionnement de la fonction]
[data <text> -> Quels paramètres sont nécessaires à la fonction et pourquoi]
[desc <text> -> Comment la fonction fonctionne]
[vars -> En-dessous de ceci se trouve toutes les déclarations de variables locales utilisées par la fonction]
fx_start
<instructions>
end
```

Examples :
```
fx bool estMultiple int n int x
data Deux entiers n et x
results Renvoie si x est un diviseur de n
fx_start
return n % x == 0
end

fx void dessineLigne int n char c
data Un entier positif n qui indique la longueur de la ligne ; un caractère c indiquant quel caractère utiliser dans le remplissage de la ligne.
desc Dessine une ligne de c de longueur n
vars
int i
fx_start
for i 0 n
print c
end
print "(ENDL)"
end
```

### Available Functions / Fonctions Disponibles
***ENGLISH***
Three functions are available and can be used all throughout the code.
- `aleatoire()`, which is the equivalent of C's *rand()* function
- `puissance(x, n)`, which is the equivalent of C's *pow()* function
- `racine(x)`, which is the equivalent of C's *sqrt()* function

***FRANÇAIS***
Trois fonctions sont disponibles et utilisables à travers votre code.
- `aleatoire()`, l'équivalent de la fonction *rand()* de C. Renvoie un nombre aléatoire.
- `puissance(x, n)`, l'équivalent de la fonction *pow()* de C. Renvoie la puissance de x par n.
- `racine(x)`, l'équivalent de la fonction *sqrt()* de C. Renvoie la racine de x.

## Commands / Commandes
***ENGLISH***
You can use commands to have an effect on your code. These commands are triggered by using the command symbol key (`:` by default), followed by the key assigned to it, then hitting Enter.<br>
The commands are, but not limited to (plugins can add some) :
- `:q` - Quit : Exits the editor **without saving**.
- `:c` - Compile : Compiles your code into algorithmic code. **Copies the program to the clipboard, overriding what may be inside.**
- `:t` - Modify tab char : Allows you to type in a new string to replace the default tab character (`\t`) for the transpilations.
- `:s` - Save : Saves the program **to your clipboard**. This will be changed in the future.
- `:o` - Open : Opens a program **from your clipboard**, ***and overwrites the old one without saving***. This will be changed in the future.
- `:p` - Compile to C++ : Transpiles your code into C++. **Copies the program to the clipboard, overriding what may be inside.** *Note that the transpilation isn't perfect, it is more of a means to test your algorithm quickly than having to rewrite it entirely in another language.*
- `:j` - Toggle namespace std : Toggles whether to use the `std` namespace in the C++ code. If true, all `std::` calls will be replaced by a `using namespace std;` at the top of the program. False by default.
- `:h` - Commands list : Lists all existing commands, either built-in or from plugins.

***FRANÇAIS***
Vous pouvez utiliser des commandes qui auront un effet syr votre code. Ces commandes sont déclenchées par l'appui sur la touche du symbole de commande (`:` par défaut), suivi de la touche assignée, puis par l'appui sur la touche Entrée.<br>
Les commades sont, mais pas limitées à (les plugins peuvent en ajouter) :
- `:q` - Quitter : Ferme l'éditeur **sans sauvegarder**.
- `:c` - Compiler : Transcrire le code en algorithmique. **Copie le programme dans le presse-papiers, réécrivant ce qui pourrait être dedans.**
- `:t` - Modifier le caractère de tabulation : Permet de taper un nouveau texte pour remplacer le caractère de tabulation par défaut (`\t`) pour les transcription.
- `:s` - Sauvegarder : Sauvegarde le programme **dans le presse-papiers**. Cela sera changé dans le futur.
- `:o` - Ouvrir : Ouvre le programme **depuis le presse-papiers**, ***et réécris par-dessus l'ancien sans le sauvegarder***. Cela sera changé dans le futur.
- `:p` - Compiler vers C++ : Transcrit votre code en C++. **Copie le programme dans le presse-papiers, réécrivant ce qui pourrait être dedans.** *Notez que la transcription n'est pas parfaite, il s'agit plus de tester votre algorithme rapidement plutôt que d'avoir à le réécrire entièrement dans un autre langage.*
- `:j` - Basculer namespace std : Bascule l'utilisation du namespace `std`dans le code C++. Si vrai, tous les appels à `std::` seront replacés par un `using namespace std;` au sommet du programme. Faux par défaut.
- `:h` - Liste des commandes : Liste toutes les commandes existantes, qu'elles soient par défaut ou proviennent de plugins.

## Plugins
See [in the plugins repository](https://github.com/megat69/AlgorithmicEditor_Plugins) on how to create a plugin.

***ENGLISH***<br>
Plugins are a great tool offered to you by the editor, and allow to extend its functionality with official or third-party applets.<br>
They can add custom commands, custom behaviour, custom syntax highlighting, and much, much more.<br>
As of today, official plugins include, but are not restricted to :
- `autocomplete`, a plugin granting you access to autocompletion in the editor ;
- `ctrl_del`, a plugin giving you access to a command able to erase the current word in one keystroke, like the Ctrl + Del keybind ;
- `docstring`, which automatically setups information for functions in a single keybind ;
- `paste`, which lets you paste anything from your clipboard to the editor ;
- **And most importantly,** `plugin_repo`, which is the heart of the plugins : it allows you to manage (enable/disable/delete/list) your plugins or download/updates new ones.
  - It is the only plugin downloaded by default (if you select so in the setup).

***FRANÇAIS***<br>
Les plugins sont d'excellents outils proposés par l'éditeur, et vous permesttent d'étendre ses fonctionnalités avec des applets officiels ou tiers.<br>
Ces derniers peuvent ajouter des commandes personnalisées, de la logique personnalisée, une coloration syntaxique personnalisée, et bien plus encore.<br>
Au moment de l'écriture de ces lignes, les plugins officiels contiennent, mais ne sont pas restreints à :
- `autocomplete`, un plugin vous donnant accès à une autocomplétion dans l'éditeur ;
- `ctrl_del`, un plugin vous donnant accès à une commande capable d'effacer le mot sélectionné en une touche, comme le raccourci Ctrl + RetourArrière ;
- `docstring`, qui vous met en place automatiquement les informations demandées pour la création de fonctions (Données, préconditions, etc.) en une seule touche ;
- `paste`, qui vous permet de coller n'importe quoi de votre presse-papiers dans l'éditeur ;
- **Et le plus important,** `plugin_repo`, qui est au coeur de tous les plugins : il vous permet de gérer (activer/désactiver/supprimmer/lister) vos plugins, ou d'en télécharger/mettre à jour d'autres.
  - Il s'agit du seul plugin téléchargé par défaut (si vous acceptez durant le setup).


**NOTE :** Even though this software supports Python 3.7 and above, every plugin might require a newer version of Python, so read their documentation carefully.
