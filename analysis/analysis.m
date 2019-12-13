data = readtable("C:\Users\Jakob\Documents\GitHub\project-opies-controller\analysis\speedanalysis\Thu_Dec_12_102225_2019_0p16\Thu_Dec_12_102225_2019.csv");
hold on;
x = data.x;
y = data.y;
time = data.Var1;



a_y = data.a_y;
a_x = data.a_x;


ax = linspace(mean(y)-3*std(y), mean(y)+3*std(y), 1000);

histogram(y, 100, 'Normalization', 'pdf')

pd = fitdist(y,'Normal');
y_approx = pdf(pd, ax);
plot(ax, y_approx)

%%
hold off

plot(time(50:end), a_y(50:end))

var(a_y(50:end))


plot(time, y)