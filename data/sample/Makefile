CC=gcc
CFLAGS=-finstrument-functions -g -O0 -ldl
TARGET=program

OBJS=main.o foo.o bar.o baz.o \
qux.o spam.o ham.o sausage.o eggs.o bacon.o dest.o
INJECTION_OBJ=injection.o

all: $(TARGET)

$(TARGET): $(OBJS) $(INJECTION_OBJ)
	$(CC) $(CFLAGS) -rdynamic $^ -o $@

$(INJECTION_OBJ): ../injection/injection.c
	$(CC) $(CFLAGS) -c $^

main.o: main.c
	$(CC) $(CFLAGS) -c $^

foo.o: foo.c
	$(CC) $(CFLAGS) -c $^

bar.o: bar.c
	$(CC) $(CFLAGS) -c $^

baz.o: baz.c
	$(CC) $(CFLAGS) -c $^

qux.o: qux.c
	$(CC) $(CFLAGS) -c $^

spam.o: spam.c
	$(CC) $(CFLAGS) -c $^

ham.o: ham.c
	$(CC) $(CFLAGS) -c $^

eggs.o: eggs.c
	$(CC) $(CFLAGS) -c $^

sausage.o: sausage.c
	$(CC) $(CFLAGS) -c $^

bacon.o: bacon.c
	$(CC) $(CFLAGS) -c $^

dest.o: dest.c
	$(CC) $(CFLAGS) -c $^

clean:
	rm -f $(OBJS)
	rm -f $(INJECTION_OBJ)
	rm -f "finstrument.txt"

