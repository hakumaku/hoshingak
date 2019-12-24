#include "ham.h"
#include "dest.h"

void ham_a(void)
{
	ham_b();
}

void ham_b(void)
{
	ham_c();
}

void ham_c(void)
{
	ham_d();
}

void ham_d(void)
{
	dest_b();
}

