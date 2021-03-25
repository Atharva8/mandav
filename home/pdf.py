from weasyprint import HTML

HTML(r'home\templates\admin\pay_summary_change_list.html').write_pdf('pp.pdf')