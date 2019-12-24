#include <stdio.h>
#include "foo.h"
#include "bar.h"
#include "baz.h"
#include "qux.h"
#include "spam.h"
#include "ham.h"
#include "eggs.h"
#include "sausage.h"
#include "bacon.h"

int main(int argc, const char *argv[])
{
	foo_a();
	foo_a();
	foo_a();
	bar_a();
	bar_a();
	bar_a();
	baz_a();
	baz_a();
	baz_a();

	/*
	qux_a();
	spam_a();
	ham_a();
	qux_a();
	spam_a();
	ham_a();
	qux_a();
	spam_a();
	ham_a();

	eggs_a();
	sausage_a();
	bacon_a();
	eggs_a();
	sausage_a();
	bacon_a();
	eggs_a();
	sausage_a();
	bacon_a();
	*/

	return 0;
}

