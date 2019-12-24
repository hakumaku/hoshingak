#include "eggs.h"
#include "dest.h"

void eggs_a(void)
{
	eggs_b();
}

void eggs_b(void)
{
	eggs_c();
}

void eggs_c(void)
{
	eggs_d();
}

void eggs_d(void)
{
	dest_c();
}

