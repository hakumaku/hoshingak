#include "baz.h"
#include "dest.h"

void baz_a(void)
{
	baz_b();
}

void baz_b(void)
{
	baz_c();
}

void baz_c(void)
{
	baz_d();
}

void baz_d(void)
{
	dest_a();
}

