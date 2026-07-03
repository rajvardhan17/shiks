#!/usr/bin/env python3
"""Test script for enhanced fee extraction functionality."""

from extractors.common import (
    extract_total_fees,
    extract_registration_fees,
    extract_tuition_fees,
    extract_admission_fees,
    extract_all_fee_types,
    extract_courses,
    extract_cutoffs,
    extract_course_details,
    parse_course_detail_text,
)

# Test samples
test_samples = [
    {
        "name": "Sample 1: Total fees with course",
        "text": """
        B.Tech in Computer Science
        Total Course Fees: Rs. 8,50,000 per year
        Registration Fee: Rs. 5,000
        Admission Fee: Rs. 2,000
        Cutoff: JEE Main 2024 - 95 percentile
        """,
    },
    {
        "name": "Sample 2: MBA program fees",
        "text": """
        MBA Program
        Total Fees: INR 20,00,000
        Tuition Fee: Rs. 15,00,000
        Registration Charges: Rs. 50,000
        Entrance Fee: Rs. 1,000
        Cutoff: CAT Score - 99 percentile
        Opening Rank: 500
        Closing Rank: 5000
        """,
    },
    {
        "name": "Sample 3: Multiple courses table",
        "text": """
        | Course | Total Fees | Registration | Cutoff |
        |--------|-----------|--------------|--------|
        | BCA | Rs. 3,00,000 | Rs. 1,500 | 70% |
        | B.Sc | Rs. 2,50,000 | Rs. 1,000 | 60% |
        | M.Tech | Rs. 5,00,000 | Rs. 2,500 | 80% |
        """,
    },
    {
        "name": "Sample 4: Mixed format",
        "text": """
        Our B.E. program costs Rs. 15 lakhs total. 
        The registration fee is Rs. 5,000 and admission fee is Rs. 2,500.
        Tuition fees are Rs. 14,92,500.
        Cutoff for JEE Advanced: 5000-8000 rank
        """,
    },
]

def run_tests():
    """Run comprehensive tests on fee extraction."""
    print("=" * 80)
    print("ENHANCED FEE EXTRACTION TEST SUITE")
    print("=" * 80)
    
    for sample in test_samples:
        print(f"\n{'*' * 80}")
        print(f"Test: {sample['name']}")
        print(f"{'*' * 80}")
        print(f"\nInput Text:\n{sample['text']}")
        print(f"\n{'-' * 80}")
        
        text = sample['text']
        
        # Test individual fee type extraction
        print("\n1. FEE TYPE EXTRACTION:")
        total = extract_total_fees(text)
        registration = extract_registration_fees(text)
        tuition = extract_tuition_fees(text)
        admission = extract_admission_fees(text)
        
        print(f"   Total Fees: {total}")
        print(f"   Registration Fees: {registration}")
        print(f"   Tuition Fees: {tuition}")
        print(f"   Admission Fees: {admission}")
        
        # Test comprehensive fee extraction
        print("\n2. COMPREHENSIVE FEE EXTRACTION:")
        all_fees = extract_all_fee_types(text)
        for fee_type, values in all_fees.items():
            if values:
                print(f"   {fee_type}: {values}")
        
        # Test course extraction
        print("\n3. COURSE EXTRACTION:")
        courses = extract_courses(text)
        print(f"   Courses Found: {courses}")
        
        # Test cutoff extraction
        print("\n4. CUTOFF EXTRACTION:")
        cutoffs = extract_cutoffs(text)
        print(f"   Cutoffs Found: {cutoffs}")
        
        # Test course details
        print("\n5. COURSE DETAILS EXTRACTION:")
        details = extract_course_details(text)
        if details:
            for detail in details:
                print(f"   - {detail}")
        else:
            print("   No course details found")
        
        # Test parsing
        if details:
            print("\n6. PARSED COURSE DETAILS:")
            for detail in details:
                parsed = parse_course_detail_text(detail)
                print(f"   Course: {parsed.get('course')}")
                print(f"   - Total Fees: {parsed.get('total_fees')}")
                print(f"   - Registration Fees: {parsed.get('registration_fees')}")
                print(f"   - Tuition Fees: {parsed.get('tuition_fees')}")
                print(f"   - Admission Fees: {parsed.get('admission_fees')}")
                print(f"   - Rankings: {parsed.get('rankings')}")
                print(f"   - Cutoffs: {parsed.get('cutoffs')}")
                if parsed.get('other_details'):
                    print(f"   - Other: {parsed.get('other_details')}")

if __name__ == "__main__":
    run_tests()
    print(f"\n{'=' * 80}")
    print("TEST SUITE COMPLETE")
    print(f"{'=' * 80}\n")
