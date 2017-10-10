PREFIX := .compiled

.PHONY = all clean xclip pbcopy

all: game.hex

$(PREFIX)/font.8o $(PREFIX)/font-data.8o: Makefile generate-font.py assets/font/5.font
		./generate-font.py assets/font/5.font font 1100 $(PREFIX)

game.8o: \
	Makefile assets/* sources/*.8o \
	$(PREFIX)/font.8o $(PREFIX)/font_data.8o \

		cat sources/main.8o > $@
		cat $(PREFIX)/font.8o >> $@
		cat $(PREFIX)/font_data.8o >> $@

game.bin: game.8o
	./octo/octo game.8o $@

game.hex: game.bin ./generate-hex.py
	./generate-hex.py game.bin $@

xclip: game.hex
	cat game.hex | xclip

pbcopy: game.hex
	cat game.hex | pbcopy

clean:
		rm -f game.bin game.8o game.hex .compiled/*
