/* tes5.c
 * Copyright (C) 2008 梅濁酒 umedoblock
 */

#include <GL/gl.h>
#include <GL/glut.h>

int ww, hh;
void display(void)
{
    float w[3][2] = {
        {0.0, -0.9},
        {-0.9, 0.9},
        {0.9, 0.9}
    };
    float x, y;
    int i, j, xx, yy;
    int width = ww, height = hh;

    glClearColor(0, 0, 0, 0);
    glClear(GL_COLOR_BUFFER_BIT);

    glEnable(GL_LINE_STIPPLE);
    glLineStipple(1, 0xf0f0);

    glBegin(GL_LINES);
    for(i=0;i<3;i++){
        glColor3f((i+3)==3, (i+2)==3, (i+1)==3);
        j = (i+1)%3;
        x = w[i][0]; y = w[i][1];
        xx = width * x;
        yy = height * y;
        glVertex2f(x, y);
        x = w[j][0]; y = w[j][1];
        glVertex2f(x, y);
    }
    glEnd();
    //glRectf(-0.1, 0.1, 0.1, -0.1);
    glPointSize(6.0);
    glBegin(GL_POINTS);
    for(i=0;i<3;i++){
        glColor3f((i+3)==3, (i+2)==3, (i+1)==3);
        x = w[i][0]; y = w[i][1];
        glVertex2f(x, y);
    }
    glEnd();
    glFlush();
}
int main(int argc , char *argv[])
{
    int width, height, num;

    if (argc >= 2){
        num = atoi(argv[1]);
    }else{
        num = 500;
    }

    ww = hh = width = height = num;

    glutInit(&argc , argv);
    glutInitWindowPosition(0, 0);
    glutInitWindowSize(width, height);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA);

    glutCreateWindow(argv[0]);
    glutDisplayFunc(display);

    glutMainLoop();
    return 0;
}
