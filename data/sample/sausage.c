#include "sausage.h"
#include "dest.h"

void sausage_a(void)
{
	sausage_b();
}

void sausage_b(void)
{
	sausage_c();
}

void sausage_c(void)
{
	sausage_d();
}

void sausage_d(void)
{
	dest_c();
}

