#include "bacon.h"
#include "dest.h"

void bacon_a(void)
{
	bacon_b();
}

void bacon_b(void)
{
	bacon_c();
}

void bacon_c(void)
{
	bacon_d();
}

void bacon_d(void)
{
	dest_c();
}

