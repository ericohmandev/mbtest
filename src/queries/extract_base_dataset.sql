SELECT 
    a.company,
    a.sector,
    a.country,
    a.fund,
    a.entry_year,
    a.exit_year,
    a.cleaned_url,
    a.is_divestment,
    a.management,
    a.board_of_directors,
    a.eqt_company_id,
    b.uuid,
    b.homepage_url,
    b.country_code,
    b.city,
    b.founded_on,
    b.short_description,
    b.employee_count,
    b.num_funding_rounds,
    b.last_funding_on,
    b.total_funding_usd
FROM portfolio_deduped a
LEFT JOIN
organisation_deduped_subset b
USING (cleaned_url)