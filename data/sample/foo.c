#include "foo.h"
#include "dest.h"

void foo_a(void)
{
	foo_b();
}

void foo_b(void)
{
	foo_c();
}

void foo_c(void)
{
	foo_d();
}

void foo_d(void)
{
	dest_a();
}

