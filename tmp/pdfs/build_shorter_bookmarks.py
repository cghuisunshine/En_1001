"""Build a navigable outline from the anthology's printed contents pages."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "shorter.pdf"
OUTPUT = ROOT / "output/pdf/shorter_bookmarked.pdf"
DATA = ROOT / "tmp/pdfs/shorter_bookmarks.info"

# Printed Arabic page 1 is PDF page 31. Front matter uses Roman numbering.
front = [
    (1, "Contents", 7),
    (1, "Chronological Table of Contents", 13),
    (1, "Preface", 15),
    (1, "Writing about Fiction", 19),
]

# Entries transcribed from the anthology's contents, in page order.
stories = [
    (1, "Silent Snow, Secret Snow — Conrad Aiken"),
    (14, "Jason Who Will Be Famous — Dorothy Allison"),
    (21, "I Want to Know Why — Sherwood Anderson"),
    (28, "Death by Landscape — Margaret Atwood"),
    (41, "Sonny's Blues — James Baldwin"),
    (64, "Gorilla, My Love — Toni Cade Bambara"),
    (69, "Letter to the Lady of the House — Richard Bausch"),
    (76, "Snow — Ann Beattie"),
    (78, "An Occurrence at Owl Creek Bridge — Ambrose Bierce"),
    (85, "Pierre Menard, Author of the Quixote — Jorge Luis Borges"),
    (93, "Miriam — Truman Capote"),
    (102, "Cathedral — Raymond Carver"),
    (113, "Paul's Case — Willa Cather"),
    (128, "The Enormous Radio — John Cheever"),
    (137, "Gusev — Anton Chekhov"),
    (147, "The Story of an Hour — Kate Chopin"),
    (150, "Heart of Darkness — Joseph Conrad"),
    (211, "The Open Boat — Stephen Crane"),
    (229, "A Wall of Fire Rising — Edwidge Danticat"),
    (241, "King of the Bingo Game — Ralph Ellison"),
    (249, "Matchimanito — Louise Erdrich"),
    (262, "A Rose for Emily — William Faulkner"),
    (269, "Barn Burning — William Faulkner"),
    (282, "Babylon Revisited — F. Scott Fitzgerald"),
    (298, "Great Falls — Richard Ford"),
    (310, "The Ice Wagon Going Down the Street — Mavis Gallant"),
    (327, "The Yellow Wallpaper — Charlotte Perkins Gilman"),
    (339, "Young Goodman Brown — Nathaniel Hawthorne"),
    (349, "Hills Like White Elephants — Ernest Hemingway"),
    (354, "The Conscience of the Court — Zora Neale Hurston"),
    (364, "Araby — James Joyce"),
    (368, "The Dead — James Joyce"),
    (399, "The Metamorphosis — Franz Kafka"),
    (434, "The White Horse — Yasunari Kawabata"),
    (437, "Girl — Jamaica Kincaid"),
    (439, "Hell-Heaven — Jhumpa Lahiri"),
    (453, "The Horse Dealer's Daughter — D. H. Lawrence"),
    (466, "The Ones Who Walk Away from Omelas — Ursula K. Le Guin"),
    (471, "The Garden Party — Katherine Mansfield"),
    (482, "Shiloh — Bobbie Ann Mason"),
    (493, "An Adventure in Paris — Guy de Maupassant"),
    (499, "Why I Like Country Music — James Alan McPherson"),
    (511, "Bartleby, the Scrivener — Herman Melville"),
    (538, "The Management of Grief — Bharati Mukherjee"),
    (551, "Royal Beatings — Alice Munro"),
    (567, "Miles City, Montana — Alice Munro"),
    (581, "Signs and Symbols — Vladimir Nabokov"),
    (586, "How I Contemplated the World from the Detroit House of Correction and Began My Life Over Again — Joyce Carol Oates"),
    (598, "The Things They Carried — Tim O'Brien"),
    (611, "A Good Man Is Hard to Find — Flannery O'Connor"),
    (622, "Good Country People — Flannery O'Connor"),
    (637, "Guests of the Nation — Frank O'Connor"),
    (646, "O Yes — Tillie Olsen"),
    (658, "The Used-Boy Raisers — Grace Paley"),
    (663, "El Paso — Jayne Anne Phillips"),
    (674, "The Fall of the House of Usher — Edgar Allan Poe"),
    (688, "The Jilting of Granny Weatherall — Katherine Anne Porter"),
    (695, "What Kind of Furniture Would Jesus Pick? — E. Annie Proulx"),
    (710, "Victory Lap — George Saunders"),
    (722, "Admission — Danzy Senna"),
    (738, "Gimpel the Fool — Isaac Bashevis Singer"),
    (749, "The Chrysanthemums — John Steinbeck"),
    (757, "Rules of the Game — Amy Tan"),
    (765, "The Death of Ivan Ilyich — Leo Tolstoy"),
    (805, "A&P — John Updike"),
    (811, "The Moths — Helena María Viramontes"),
    (816, "Everyday Use — Alice Walker"),
    (823, "Blackberry Winter — Robert Penn Warren"),
    (839, "A Worn Path — Eudora Welty"),
    (846, "The Use of Force — William Carlos Williams"),
    (850, "Bullet in the Brain — Tobias Wolff"),
    (854, "Kew Gardens — Virginia Woolf"),
    (860, "The Man Who Was Almost a Man — Richard Wright"),
]

writers = [
    (872, "Why Do You Write? — Margaret Atwood"),
    (872, "What Is It I Think I'm Doing Anyhow? — Toni Cade Bambara"),
    (873, "Letter to a Young Writer — Richard Bausch"),
    (877, "Preface to The Nigger of the 'Narcissus' — Joseph Conrad"),
    (879, "Letter to Barrett H. Clark — Joseph Conrad"),
    (880, "Letter to John Northern Hilliard — Stephen Crane"),
    (881, "An Interview — Ralph Ellison"),
    (883, "An Interview — Ernest Hemingway"),
    (885, "Letter to Max Brod — Franz Kafka"),
    (887, "The Novel — Guy de Maupassant"),
    (889, "A Four-Hundred-Year-Old Woman — Bharati Mukherjee"),
    (891, "The Philosophy of Composition — Edgar Allan Poe"),
    (892, "An Interview — Katherine Anne Porter"),
    (895, "What Is Art? — Leo Tolstoy"),
    (897, "Accepting the Howells Medal — John Updike"),
    (898, "An Interview — Eudora Welty"),
]

reviews = [
    (917, "Willa Cather's 'Paul's Case' — Andrea Barrett"),
    (918, "Anton Chekhov's 'Gusev' — Richard Bausch"),
    (919, "Ernest Hemingway's 'Hills Like White Elephants' — Frederick Busch"),
    (920, "Kafka's The Metamorphosis: Metamorphosis of the Metaphor — Stanley Corngold"),
    (921, "Eudora Welty's 'A Worn Path' — Susan Dodd"),
    (922, "Bharati Mukherjee's 'The Management of Grief' — Richard Ford"),
    (923, "Stephen Crane's 'The Open Boat' — Allan Gurganus"),
    (925, "Joseph Conrad's Heart of Darkness — Barry Hannah"),
    (927, "Frank O'Connor's 'Guests of the Nation' — Edward P. Jones"),
    (928, "Structure and Sympathy in Joyce's 'The Dead' — C. C. Loomis Jr."),
    (931, "Melville's Parable of the Walls — Leo Marx"),
    (933, "The Reader as Voyeur — Gary Saul Morson"),
    (934, "Review of Hawthorne's Twice-Told Tales — Edgar Allan Poe"),
    (936, "Racism and the Heart of Darkness — C. P. Sarvan"),
    (940, "[Stephen Crane: Naturalist] — Charles C. Walcutt"),
    (941, "The House of Poe — Richard Wilbur"),
]

faulkner = [
    (944, "An Interview — William Faulkner"),
    (949, "Nobel Prize Address — William Faulkner"),
    (950, "A Rose for Emily — Edmond L. Volpe"),
    (952, "The Book of the Grotesque — Sherwood Anderson"),
    (954, "From William Faulkner and Southern History — Joel Williamson"),
]

munro = [
    (956, "What Is Real? — Alice Munro"),
    (959, "From Introduction to the Vintage Edition of Selected Stories — Alice Munro"),
    (961, "From Lives of Mothers & Daughters — Sheila Munro"),
    (962, "From Alice Munro: Writing Her Lives — Robert Thacker"),
    (964, "An Appreciation — Margaret Atwood"),
    (965, "An Appreciation — Russell Banks"),
    (966, "An Appreciation — Brad Hooper"),
]

oconnor = [
    (968, "The Nature and Aim of Fiction — Flannery O'Connor"),
    (969, "The Grotesque in Southern Fiction — Flannery O'Connor"),
    (970, "From Writing Short Stories — Flannery O'Connor"),
    (972, "From The Bible Salesman — Brad Gooch"),
    (974, "Flannery O'Connor and the Modernist Ethic — Tony Magistrale"),
    (975, "Flannery O'Connor's 'A Good Man Is Hard to Find' — Lee Smith"),
    (976, "From Beyond the Peacock — Alice Walker"),
    (978, "Flannery O'Connor: A Prose Elegy — Thomas Merton"),
    (980, "A Prayer Journal — Flannery O'Connor"),
]


def bookmark(level, title, pdf_page):
    assert 1 <= pdf_page <= 1028
    assert "\n" not in title
    return f"BookmarkBegin\nBookmarkTitle: {title}\nBookmarkLevel: {level}\nBookmarkPageNumber: {pdf_page}\n"


bookmarks = [bookmark(*item) for item in front]
bookmarks.append(bookmark(1, "Stories", 31))
bookmarks += [bookmark(2, title, printed_page + 30) for printed_page, title in stories]
for section, page, entries in [
    ("Writers on Writing", 871, writers),
    ("Reviews and Commentaries", 917, reviews),
]:
    bookmarks.append(bookmark(1, section, page + 30))
    bookmarks += [bookmark(2, title, printed_page + 30) for printed_page, title in entries]
bookmarks.append(bookmark(1, "Writing Fiction", 901 + 30))
bookmarks.append(bookmark(1, "A Local Habitation and a Name: Meditations on Writing", 911 + 30))
# Move those two standalone sections into their printed order, before reviews.
writing_fiction = bookmarks.pop()
writing_fiction_2 = bookmarks.pop()
reviews_start = next(i for i, value in enumerate(bookmarks) if "BookmarkTitle: Reviews and Commentaries\n" in value)
bookmarks[reviews_start:reviews_start] = [writing_fiction_2, writing_fiction]

bookmarks.append(bookmark(1, "Authors in Depth", 944 + 30))
for author, page, entries in [
    ("William Faulkner", 944, faulkner),
    ("Alice Munro", 956, munro),
    ("Flannery O'Connor", 968, oconnor),
]:
    bookmarks.append(bookmark(2, author, page + 30))
    bookmarks += [bookmark(3, title, printed_page + 30) for printed_page, title in entries]
for title, page in [
    ("Glossary of Critical Terms", 982),
    ("Permissions Acknowledgments", 988),
    ("Index of Titles", 995),
]:
    bookmarks.append(bookmark(1, title, page + 30))

DATA.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
DATA.write_text("".join(bookmarks), encoding="utf-8")
subprocess.run(
    ["pdftk", str(SOURCE), "update_info_utf8", str(DATA), "output", str(OUTPUT)],
    check=True,
)
print(f"Wrote {OUTPUT} with {len(bookmarks)} bookmarks")
