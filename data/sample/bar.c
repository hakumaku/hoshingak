#include "bar.h"
#include "dest.h"

void bar_a(void)
{
	bar_b();
}

void bar_b(void)
{
	bar_c();
}

void bar_c(void)
{
	bar_d();
}

void bar_d(void)
{
	dest_a();
}

