#include "spam.h"
#include "dest.h"

void spam_a(void)
{
	spam_b();
}

void spam_b(void)
{
	spam_c();
}

void spam_c(void)
{
	spam_d();
}

void spam_d(void)
{
	dest_b();
}

