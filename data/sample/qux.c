#include "qux.h"
#include "dest.h"

void qux_a(void)
{
	qux_b();
}

void qux_b(void)
{
	qux_c();
}

void qux_c(void)
{
	qux_d();
}

void qux_d(void)
{
	dest_b();
}

