/* tes4.c
 * Copyright (C) 2008 梅濁酒 umedoblock
 */

#include <GL/gl.h>
#include <GL/glut.h>


void display(void)
{
    float x[3][2] = {
        {0.0, -0.9},
        {-0.9, 0.9},
        {0.9, 0.9}
    };
    int i;

    glClear(GL_COLOR_BUFFER_BIT);

    glEnable(GL_LINE_STIPPLE);
    glLineStipple(1, 0xf0f0);

    glBegin(GL_LINES);
    for(i=0;i<3;i++){
        glColor3f((i+3)==3, (i+2)==3, (i+1)==3);
        glVertex2f(x[i][0], x[i][1]);
        glVertex2f(x[(i+1)%3][0], x[(i+1)%3][1]);
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

    width = height = num;

    glutInit(&argc , argv);
    glutInitWindowPosition(0, 0);
    glutInitWindowSize(width, height);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA);

    glutCreateWindow(argv[0]);
    glutDisplayFunc(display);

    glutMainLoop();
    return 0;
}
